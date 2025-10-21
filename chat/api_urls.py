from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    UserViewSet, UserProfileViewSet, PrivateChatViewSet, 
    PrivateMessageViewSet, RoomViewSet, MessageViewSet,
    ChatAPIView, OnlineUsersAPIView, UpdateActivityAPIView
)

# Create router for ViewSets
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('profiles', UserProfileViewSet)
router.register('chats', PrivateChatViewSet, basename='privatechat')
router.register('messages', PrivateMessageViewSet, basename='privatemessage')
router.register('rooms', RoomViewSet)
router.register('room-messages', MessageViewSet)

app_name = 'chat_api'

urlpatterns = [
    # API ViewSets
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('start-chat/', ChatAPIView.as_view(), name='start_chat'),
    path('online-users/', OnlineUsersAPIView.as_view(), name='online_users'),
    path('update-activity/', UpdateActivityAPIView.as_view(), name='update_activity'),
]
