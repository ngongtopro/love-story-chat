from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth.models import User
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import UserProfile, PrivateChat, PrivateMessage, Room, Message
from .serializers import (
    UserSerializer, UserProfileSerializer, PrivateChatSerializer,
    PrivateMessageSerializer, PrivateMessageCreateSerializer,
    RoomSerializer, MessageSerializer, MessageCreateSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profiles
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['display_name', 'user__username']
    filterset_fields = ['is_online']
    ordering_fields = ['last_seen', 'created_at']
    ordering = ['-last_seen']

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """Update current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def online_users(self, request):
        """Get list of online users"""
        online_profiles = self.queryset.filter(is_online=True)
        serializer = self.get_serializer(online_profiles, many=True)
        return Response(serializer.data)


class PrivateChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for private chats
    """
    serializer_class = PrivateChatSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['updated_at', 'created_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Get chats for current user"""
        return PrivateChat.get_user_chats(self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in chat as read"""
        chat = self.get_object()
        messages = chat.messages.filter(sender__ne=request.user, is_read=False)
        for message in messages:
            message.mark_as_read()
        return Response({'status': 'messages marked as read'})

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block chat"""
        chat = self.get_object()
        chat.block_chat(request.user)
        return Response({'status': 'chat blocked'})

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Unblock chat"""
        chat = self.get_object()
        chat.unblock_chat(request.user)
        return Response({'status': 'chat unblocked'})


class PrivateMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for private messages
    """
    serializer_class = PrivateMessageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['message_type', 'is_read']
    ordering_fields = ['timestamp']
    ordering = ['timestamp']

    def get_queryset(self):
        """Get messages for current user's chats"""
        user_chats = PrivateChat.get_user_chats(self.request.user)
        return PrivateMessage.objects.filter(chat__in=user_chats)

    def get_serializer_class(self):
        if self.action == 'create':
            return PrivateMessageCreateSerializer
        return PrivateMessageSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark message as read"""
        message = self.get_object()
        if message.get_recipient() == request.user:
            message.mark_as_read()
            return Response({'status': 'message marked as read'})
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet for rooms (legacy)
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for this room"""
        room = self.get_object()
        messages = room.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for messages (legacy)
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room']
    ordering_fields = ['timestamp']
    ordering = ['timestamp']

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        serializer.save()


class ChatAPIView(APIView):
    """
    API view for starting a chat with a user
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to chat with')
            }
        ),
        responses={200: PrivateChatSerializer}
    )
    def post(self, request):
        """Start or get existing chat with a user"""
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if other_user == request.user:
            return Response({'error': 'Cannot chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        chat, created = PrivateChat.get_or_create_chat(request.user, other_user)
        serializer = PrivateChatSerializer(chat, context={'request': request})
        
        return Response({
            'chat': serializer.data,
            'created': created
        })


class OnlineUsersAPIView(APIView):
    """
    API view for getting online users
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get list of online users"""
        online_users = User.objects.filter(profile__is_online=True)
        serializer = UserSerializer(online_users, many=True)
        return Response({
            'online_users': serializer.data,
            'online_user_ids': [user.id for user in online_users]
        })


class UpdateActivityAPIView(APIView):
    """
    API view for updating user activity (heartbeat)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Update user's last activity"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.is_online = True
        profile.save()
        return Response({'status': 'activity updated'})
