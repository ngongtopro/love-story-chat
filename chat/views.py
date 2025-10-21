from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.core.cache import cache
from .models import Room, Message, PrivateChat, PrivateMessage
from caro_game.models import CaroGame
import json
import logging
import time

logger = logging.getLogger(__name__)


@login_required
def home(request):
    """Display user's private chats"""
    try:
        # Mark user as online
        user_online_key = f"user_{request.user.id}_last_seen"
        cache.set(user_online_key, time.time(), timeout=300)  # 5 minutes
    except Exception as e:
        logger.error(f"Cache error when setting user online status: {e}")
    
    # Get all users for starting new chats (excluding current user)
    all_users = User.objects.exclude(id=request.user.id).order_by('username')
    
    # Create users data with online status
    current_time = time.time()
    users_with_status = []
    for user in all_users:
        is_online = False
        try:
            user_last_seen_key = f"user_{user.id}_last_seen"
            last_seen = cache.get(user_last_seen_key)
            is_online = last_seen and (current_time - last_seen < 300)
        except Exception as e:
            logger.error(f"Cache error when getting user {user.id} online status: {e}")
        
        users_with_status.append({
            'user': user,
            'is_online': is_online,
            'id': user.id,
            'username': user.username
        })
    
    # Get current user's chats
    user_chats = PrivateChat.get_user_chats(request.user)
    
    # Prepare chat data with latest messages and other user info
    chats_data = []
    for chat in user_chats:
        print(chat)
        other_user = chat.get_other_user(request.user)
        latest_message = chat.get_latest_message()
        unread_count = chat.private_messages.filter(
            sender=other_user,
            is_read=False
        ).count()
        
        chats_data.append({
            'chat': chat,
            'other_user': other_user,
            'latest_message': latest_message,
            'unread_count': unread_count
        })
    
    return render(request, 'chat/home.html', {
        'chats_data': chats_data,
        'all_users': users_with_status,
    })


@login_required
def chat_view(request, user_id):
    """Display private chat with specific user"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Don't allow chat with self
    if other_user == request.user:
        return redirect('chat:home')
    
    # Get or create private chat
    chat, created = PrivateChat.get_or_create_chat(request.user, other_user)
    
    # Get recent messages (limit for performance)
    messages = chat.private_messages.select_related('sender').order_by('timestamp')[:100]
    
    # Mark messages as read
    chat.private_messages.filter(
        sender=other_user,
        is_read=False
    ).update(is_read=True)
    
    return render(request, 'chat/private_chat.html', {
        'chat': chat,
        'other_user': other_user,
        'messages': messages,
        'chat_id': chat.chat_id
    })


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat:home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """User profile view"""
    # Get user's chats
    user_chats = PrivateChat.get_user_chats(request.user)[:10]
    
    # Get user's recent messages
    user_messages = PrivateMessage.objects.filter(sender=request.user).select_related('chat').order_by('-timestamp')[:5]
    
    # Get message count
    message_count = PrivateMessage.objects.filter(sender=request.user).count()
    
    # Get Caro game stats
    games_won = CaroGame.objects.filter(winner=request.user).count()
    games_played = CaroGame.objects.filter(
        Q(player1=request.user) | Q(player2=request.user),
        status='finished'
    ).count()
    
    context = {
        'user_chats': user_chats,
        'user_messages': user_messages,
        'message_count': message_count,
        'games_won': games_won,
        'games_played': games_played,
    }
    
    return render(request, 'chat/profile.html', context)


@login_required
def start_chat(request, user_id):
    """Start a chat with specific user - API endpoint"""
    if request.method == 'POST':
        other_user = get_object_or_404(User, id=user_id)
        
        if other_user == request.user:
            return JsonResponse({'error': 'Cannot chat with yourself'}, status=400)
        
        chat, created = PrivateChat.get_or_create_chat(request.user, other_user)
        
        return JsonResponse({
            'success': True,
            'chat_id': chat.chat_id,
            'redirect_url': f'/chat/{user_id}/',
            'created': created
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def get_private_messages(request, user_id):
    """Get private messages with specific user via AJAX"""
    other_user = get_object_or_404(User, id=user_id)
    chat, _ = PrivateChat.get_or_create_chat(request.user, other_user)
    
    messages = chat.private_messages.select_related('sender').order_by('timestamp')
    
    message_list = []
    for message in messages:
        message_list.append({
            'id': message.id,
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_own_message': message.sender == request.user
        })
    
    return JsonResponse({'messages': message_list})


@csrf_exempt  
@login_required
def send_private_message(request, user_id):
    """Send private message via AJAX"""
    if request.method == 'POST':
        other_user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Get or create chat
        chat, _ = PrivateChat.get_or_create_chat(request.user, other_user)
        
        # Create message
        message = PrivateMessage.objects.create(
            chat=chat,
            sender=request.user,
            content=message_content
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'is_own_message': True
            }
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)













# Legacy room support (for backward compatibility)
def room(request, room_name):
    """Display a specific chat room using PostgreSQL - Legacy support"""
    # Get room
    room_obj = get_object_or_404(Room, name=room_name)
    
    # Get recent messages (limit for performance)
    messages = Message.objects.filter(room=room_obj).select_related('user').order_by('timestamp')[:100]
    
    return render(request, 'caro_game/caro_room.html', {
        'room': room_obj,
        'room_name': room_name,
        'messages': messages
    })


@login_required
def create_room(request):
    """Create a new chat room using PostgreSQL - Legacy support"""
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        room_description = request.POST.get('room_description', '')
        
        if room_name:
            # Check if room already exists
            if Room.objects.filter(name=room_name).exists():
                return render(request, 'chat/create_room.html', {
                    'error': 'Room already exists!'
                })
            
            # Create new room
            Room.objects.create(
                name=room_name,
                description=room_description,
                created_by=request.user
            )
            return redirect('chat:room', room_name=room_name)
        else:
            return render(request, 'chat/create_room.html', {
                'error': 'Room name is required!'
            })
    
    return render(request, 'chat/create_room.html')


@csrf_exempt
def get_messages(request, room_name):
    """Get messages for a room via AJAX - Legacy support"""
    if request.method == 'GET':
        try:
            room_obj = get_object_or_404(Room, name=room_name)
            messages_qs = Message.objects.filter(room=room_obj).select_related('user').order_by('timestamp')
            
            messages = []
            for message in messages_qs:
                messages.append({
                    'id': message.id,
                    'user': message.user.username,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                })
            
            return JsonResponse({'messages': messages})
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return JsonResponse({'error': 'Failed to get messages'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
@login_required
def get_online_users(request):
    """API endpoint to get online users status"""
    if request.method == 'GET':
        try:
            # Mark current user as online
            user_online_key = f"user_{request.user.id}_last_seen"
            cache.set(user_online_key, time.time(), timeout=300)  # 5 minutes
            
            # Get all users (excluding current user)
            all_users = User.objects.exclude(id=request.user.id).values('id', 'username')
            
            # Create users data with online status
            current_time = time.time()
            users_with_status = []
            online_user_ids = []
            
            for user in all_users:
                is_online = False
                try:
                    user_last_seen_key = f"user_{user['id']}_last_seen"
                    last_seen = cache.get(user_last_seen_key)
                    is_online = last_seen and (current_time - last_seen < 300)
                    if is_online:
                        online_user_ids.append(user['id'])
                except Exception as e:
                    logger.error(f"Cache error when getting user {user['id']} online status: {e}")
                
                users_with_status.append({
                    'id': user['id'],
                    'username': user['username'],
                    'is_online': is_online
                })
            
            return JsonResponse({
                'users': users_with_status,
                'online_user_ids': online_user_ids,
                'online_count': len(online_user_ids)
            })
        except Exception as e:
            logger.error(f"Error getting online users: {e}")
            return JsonResponse({'error': 'Failed to get online users'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
@login_required  
def update_user_activity(request):
    """API endpoint to update user activity (heartbeat)"""
    if request.method == 'POST':
        try:
            # Mark user as online
            user_online_key = f"user_{request.user.id}_last_seen"
            cache.set(user_online_key, time.time(), timeout=300)  # 5 minutes
            
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
            return JsonResponse({'error': 'Failed to update activity'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)