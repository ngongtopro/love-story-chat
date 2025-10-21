from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, PrivateChat, PrivateMessage, Room, Message


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    user = UserSerializer(read_only=True)
    win_rate = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'display_name', 'avatar', 'bio', 'is_online',
            'last_seen', 'total_games_played', 'total_games_won', 
            'total_messages_sent', 'win_rate', 'name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_online', 'last_seen', 'total_games_played', 
            'total_games_won', 'total_messages_sent', 'created_at', 'updated_at'
        ]


class PrivateChatSerializer(serializers.ModelSerializer):
    """Private chat serializer"""
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    chat_id = serializers.ReadOnlyField()
    latest_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PrivateChat
        fields = [
            'id', 'user1', 'user2', 'chat_id', 'is_active', 
            'is_blocked_by_user1', 'is_blocked_by_user2',
            'latest_message', 'unread_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_message(self, obj):
        latest = obj.get_latest_message()
        if latest:
            return PrivateMessageSerializer(latest, context=self.context).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_unread_count(request.user)
        return 0


class PrivateMessageSerializer(serializers.ModelSerializer):
    """Private message serializer"""
    sender = UserSerializer(read_only=True)
    recipient = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PrivateMessage
        fields = [
            'id', 'chat', 'sender', 'recipient', 'content', 'message_type',
            'attachment', 'is_read', 'read_at', 'timestamp'
        ]
        read_only_fields = ['id', 'sender', 'timestamp', 'read_at']
    
    def get_recipient(self, obj):
        return UserSerializer(obj.get_recipient()).data


class PrivateMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating private messages"""
    recipient_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PrivateMessage
        fields = ['content', 'message_type', 'attachment', 'recipient_id']
    
    def create(self, validated_data):
        recipient_id = validated_data.pop('recipient_id')
        sender = self.context['request'].user
        
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient not found")
        
        # Get or create private chat
        chat, created = PrivateChat.get_or_create_chat(sender, recipient)
        
        # Create message
        message = PrivateMessage.objects.create(
            chat=chat,
            sender=sender,
            **validated_data
        )
        
        return message


class RoomSerializer(serializers.ModelSerializer):
    """Room serializer (legacy)"""
    created_by = UserSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'created_by', 'message_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class MessageSerializer(serializers.ModelSerializer):
    """Message serializer (legacy)"""
    user = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'user', 'content', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages in rooms"""
    room_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Message
        fields = ['content', 'room_id']
    
    def create(self, validated_data):
        room_id = validated_data.pop('room_id')
        user = self.context['request'].user
        
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room not found")
        
        message = Message.objects.create(
            room=room,
            user=user,
            **validated_data
        )
        
        return message
