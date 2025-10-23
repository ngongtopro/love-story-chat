from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'chat'

urlpatterns = [
    # Private Chat URLs
    path('chat/<int:user_id>/', views.chat_view, name='chat_view'),
    path('start-chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('api/private-messages/<int:user_id>/', views.get_private_messages, name='get_private_messages'),
    path('api/send-message/<int:user_id>/', views.send_private_message, name='send_private_message'),
    
    # Online Status APIs
    path('api/online-users/', views.get_online_users, name='get_online_users'),
    path('api/update-activity/', views.update_user_activity, name='update_user_activity'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    
    # Legacy Room URLs (backward compatibility)
    path('room/<str:room_name>/', views.room, name='room'),
    path('create-room/', views.create_room, name='create_room'),
    path('api/messages/<str:room_name>/', views.get_messages, name='get_messages'),
]