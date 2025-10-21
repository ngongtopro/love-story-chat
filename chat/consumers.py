from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Room, Message
from caro_game.models import CaroGame
import json
import logging

logger = logging.getLogger(__name__)


class HomeConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for home page to handle real-time room updates"""
    
    async def connect(self):
        self.room_group_name = 'home_updates'
        
        # Join home updates group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark user as online if authenticated
        if self.scope['user'] and self.scope['user'].is_authenticated:
            await self.update_user_online_status(True)
        
        # Send current rooms list and online users on connect
        rooms = await self.get_rooms()
        await self.send(text_data=json.dumps({
            'type': 'rooms_list',
            'rooms': rooms
        }))
        
        # Send current online users
        online_users = await self.get_online_users()
        room_data = await self.get_room_stats()
        await self.send(text_data=json.dumps({
            'type': 'online_users_update',
            'online_users': online_users
        }))
        await self.send(text_data=json.dumps({
            'type': 'room_update',
            'room_data': room_data
        }))
        
        # Broadcast to other users that someone came online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status_changed',
                'user_id': self.scope['user'].id if self.scope['user'].is_authenticated else None
            }
        )
    
    async def disconnect(self, close_code):
        # Mark user as offline if authenticated
        if self.scope['user'] and self.scope['user'].is_authenticated:
            await self.update_user_online_status(False)
            
            # Broadcast to other users that someone went offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status_changed',
                    'user_id': self.scope['user'].id
                }
            )
        
        # Leave home updates group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_rooms':
                rooms = await self.get_rooms()
                await self.send(text_data=json.dumps({
                    'type': 'rooms_list',
                    'rooms': rooms
                }))
            elif message_type == 'get_online_users':
                online_users = await self.get_online_users()
                room_data = await self.get_room_stats()
                await self.send(text_data=json.dumps({
                    'type': 'online_users_update',
                    'online_users': online_users
                }))
                await self.send(text_data=json.dumps({
                    'type': 'room_update',
                    'room_data': room_data
                }))
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in HomeConsumer WebSocket")
        except Exception as e:
            logger.error(f"Error in HomeConsumer WebSocket receive: {e}")
    
    async def user_status_changed(self, event):
        """Handle user online/offline status change"""
        online_users = await self.get_online_users()
        room_data = await self.get_room_stats()
        
        await self.send(text_data=json.dumps({
            'type': 'online_users_update',
            'online_users': online_users
        }))
        await self.send(text_data=json.dumps({
            'type': 'room_update', 
            'room_data': room_data
        }))
    
    @database_sync_to_async
    def update_user_online_status(self, is_online):
        """Update user's online status in cache"""
        try:
            from django.core.cache import cache
            import time
            
            if self.scope['user'] and self.scope['user'].is_authenticated:
                user_online_key = f"user_{self.scope['user'].id}_last_seen"
                
                if is_online:
                    cache.set(user_online_key, time.time(), timeout=300)  # 5 minutes
                else:
                    cache.delete(user_online_key)
                    
        except Exception as e:
            logger.error(f"Error updating user online status: {e}")
    
    async def room_created(self, event):
        """Handle room created event"""
        await self.send(text_data=json.dumps({
            'type': 'room_created',
            'room': event['room']
        }))
    
    async def room_updated(self, event):
        """Handle room updated event"""
        rooms = await self.get_rooms()
        await self.send(text_data=json.dumps({
            'type': 'rooms_list',
            'rooms': rooms
        }))
    
    @database_sync_to_async
    def get_rooms(self):
        """Get filtered rooms based on user permissions"""
        try:
            from django.core.cache import cache
            import time
            
            rooms = Room.objects.select_related('created_by').order_by('-created_at')
            rooms_data = []
            current_time = time.time()
            
            for room in rooms:
                # Get online users for this room
                online_users_key = f"room_{room.name}_online_users"
                online_users = cache.get(online_users_key, {})
                
                # Clean up expired users (older than 5 minutes)
                active_users = {}
                for username, last_seen in online_users.items():
                    if current_time - last_seen < 300:  # 5 minutes
                        active_users[username] = last_seen
                
                # Update cleaned cache
                if active_users != online_users:
                    cache.set(online_users_key, active_users, timeout=300)
                
                # Check if current user is in this room
                current_user_in_room = self.scope['user'].username in active_users
                
                # Check if room is empty
                room_is_empty = len(active_users) == 0
                
                # Check if current user created this room
                current_user_created_room = room.created_by == self.scope['user']
                
                # Check if user has ever joined this room (joined rooms history)
                joined_rooms_key = f"user_{self.scope['user'].id}_joined_rooms"
                user_joined_rooms = cache.get(joined_rooms_key, set())
                user_has_joined_room = room.name in user_joined_rooms
                
                # Show room if: 
                # 1. User is currently in the room OR 
                # 2. Room is empty OR 
                # 3. User created this room (always show rooms you created) OR
                # 4. User has previously joined this room (show rooms you've been in)
                if current_user_in_room or room_is_empty or current_user_created_room or user_has_joined_room:
                    rooms_data.append({
                        'id': room.id,
                        'name': room.name,
                        'description': room.description or '',
                        'created_by': room.created_by.username,
                        'created_at': room.created_at.strftime('%B %d, %Y'),
                        'created_at_iso': room.created_at.isoformat(),
                        'online_users_count': len(active_users),
                        'user_is_in_room': current_user_in_room,
                        'user_created_room': current_user_created_room,
                        'user_has_joined_room': user_has_joined_room,
                        'is_empty': room_is_empty,
                    })
            
            return rooms_data
        except Exception as e:
            logger.error(f"Error getting filtered rooms: {e}")
            return []

    @database_sync_to_async
    def get_online_users(self):
        """Get list of online user IDs"""
        try:
            from django.core.cache import cache
            import time
            
            # Get all users who have been active in the last 5 minutes
            online_users = []
            current_time = time.time()
            
            # Check all cached online user data
            from django.contrib.auth.models import User
            users = User.objects.all()
            
            for user in users:
                user_online_key = f"user_{user.id}_last_seen"
                last_seen = cache.get(user_online_key)
                
                if last_seen and (current_time - last_seen < 300):  # 5 minutes
                    online_users.append(user.id)
            
            return online_users
        except Exception as e:
            logger.error(f"Error getting online users: {e}")
            return []

    @database_sync_to_async
    def get_room_stats(self):
        """Get room and game statistics"""
        try:
            from django.core.cache import cache
            import time
            
            current_time = time.time()
            
            # Count active rooms (rooms with users online in the last 5 minutes)
            rooms = Room.objects.all()
            active_rooms = 0
            
            for room in rooms:
                online_users_key = f"room_{room.name}_online_users"
                online_users = cache.get(online_users_key, {})
                
                # Check if any users are still active
                active_users = {username: last_seen for username, last_seen in online_users.items() 
                              if current_time - last_seen < 300}
                
                if active_users:
                    active_rooms += 1
            
            # Count active caro games
            active_games = CaroGame.objects.filter(status='active').count()
            
            return {
                'active_rooms': active_rooms,
                'active_games': active_games
            }
        except Exception as e:
            logger.error(f"Error getting room stats: {e}")
            return {'active_rooms': 0, 'active_games': 0}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Add user to online users and notify others
        if self.user.is_authenticated:
            await self.add_user_to_room()
            
            # Send current online users list to the newly connected user
            online_users = await self.get_online_users()
            await self.send(text_data=json.dumps({
                'type': 'online_users',
                'users': online_users
            }))

    async def disconnect(self, close_code):
        # Remove user from online users and notify others
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.remove_user_from_room()
            
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'chat')
            
            if message_type == 'chat':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'caro':
                await self.handle_caro_event(text_data_json)
            elif message_type == 'heartbeat':
                await self.handle_heartbeat(text_data_json)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in WebSocket")
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {e}")

    async def handle_heartbeat(self, data):
        """Handle heartbeat to maintain online status"""
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.set_user_online()
            logger.debug(f"Heartbeat received from {self.user.username} in room {self.room_name}")

    async def handle_chat_message(self, data):
        """Handle regular chat messages"""
        message = data.get('message', '')
        username = data.get('username', 'Anonymous')

        if message.strip():
            # Save message to PostgreSQL database
            await self.save_message(username, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )

    async def handle_caro_event(self, data):
        """Handle Caro game events"""
        action = data.get('action')
        
        if action == 'game_created':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'caro_game_created',
                    'game': data.get('game'),
                    'creator': data.get('creator')
                }
            )
        elif action == 'game_joined':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'caro_game_joined',
                    'game': data.get('game'),
                    'player': data.get('player')
                }
            )
        elif action == 'move_made':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'caro_move_made',
                    'game': data.get('game'),
                    'row': data.get('row'),
                    'col': data.get('col'),
                    'player': data.get('player')
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

    @database_sync_to_async
    def save_message(self, username, message):
        """Save message to PostgreSQL database"""
        try:
            user = User.objects.get(username=username)
            room, created = Room.objects.get_or_create(
                name=self.room_name,
                defaults={'created_by': user}
            )
            Message.objects.create(
                user=user,
                room=room,
                content=message
            )
            logger.info(f"Message saved to PostgreSQL: {username} in {self.room_name}")
        except User.DoesNotExist:
            logger.error(f"User {username} does not exist")
        except Exception as e:
            logger.error(f"Error saving message to PostgreSQL: {e}")

    # Caro game event handlers
    async def caro_game_created(self, event):
        """Send game created event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'caro',
            'action': 'game_created',
            'game': event['game'],
            'creator': event['creator']
        }))

    async def caro_game_joined(self, event):
        """Send game joined event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'caro',
            'action': 'game_joined',
            'game': event['game'],
            'player': event['player']
        }))

    async def caro_move_made(self, event):
        """Send move made event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'caro',
            'action': 'move_made',
            'game': event['game'],
            'row': event['row'],
            'col': event['col'],
            'player': event['player']
        }))

    # Online Users Tracking Methods
    async def add_user_to_room(self):
        """Add user to online users list and notify room"""
        online_users = await self.get_online_users()
        
        # Add current user if not already in list
        if self.user.username not in [user['username'] for user in online_users]:
            await self.set_user_online()
            
        # Track that user has joined this room for future visibility
        await self.track_user_joined_room()
            
        # Get updated list and broadcast
        online_users = await self.get_online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_users_updated',
                'users': online_users
            }
        )
        
        logger.info(f"User {self.user.username} joined room {self.room_name}")

    @database_sync_to_async
    def track_user_joined_room(self):
        """Track that user has joined this room for visibility purposes"""
        from django.core.cache import cache
        
        # Store in joined rooms history for this user
        joined_rooms_key = f"user_{self.user.id}_joined_rooms"
        user_joined_rooms = cache.get(joined_rooms_key, set())
        
        # Add current room to the set
        if isinstance(user_joined_rooms, list):
            user_joined_rooms = set(user_joined_rooms)
        user_joined_rooms.add(self.room_name)
        
        # Store back in cache (expires in 7 days)
        cache.set(joined_rooms_key, user_joined_rooms, timeout=604800)  # 7 days
        
        logger.info(f"Tracked user {self.user.username} joined room {self.room_name}")

    async def remove_user_from_room(self):
        """Remove user from online users list and notify room"""
        await self.set_user_offline()
        
        # Get updated list and broadcast
        online_users = await self.get_online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_users_updated',
                'users': online_users
            }
        )
        
        logger.info(f"User {self.user.username} left room {self.room_name}")

    async def online_users_updated(self, event):
        """Send updated online users list to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'users': event['users']
        }))

    @database_sync_to_async
    def get_online_users(self):
        """Get list of online users in this room"""
        from django.core.cache import cache
        
        online_users_key = f"room_{self.room_name}_online_users"
        online_users = cache.get(online_users_key, {})
        
        # Clean up expired users (older than 5 minutes)
        import time
        current_time = time.time()
        active_users = {}
        
        for username, last_seen in online_users.items():
            if current_time - last_seen < 300:  # 5 minutes
                active_users[username] = last_seen
        
        # Save cleaned up list
        cache.set(online_users_key, active_users, timeout=300)
        
        # Convert to list format for frontend
        users_list = []
        for username in active_users.keys():
            users_list.append({
                'username': username,
                'is_current_user': username == self.user.username
            })
        
        return users_list

    @database_sync_to_async
    def set_user_online(self):
        """Mark user as online in this room"""
        from django.core.cache import cache
        import time
        
        online_users_key = f"room_{self.room_name}_online_users"
        online_users = cache.get(online_users_key, {})
        online_users[self.user.username] = time.time()
        cache.set(online_users_key, online_users, timeout=300)

    @database_sync_to_async
    def set_user_offline(self):
        """Mark user as offline in this room"""
        from django.core.cache import cache
        
        online_users_key = f"room_{self.room_name}_online_users"
        online_users = cache.get(online_users_key, {})
        if self.user.username in online_users:
            del online_users[self.user.username]
            cache.set(online_users_key, online_users, timeout=300)


class PrivateChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for private chat between two users"""
    
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'private_chat_{self.chat_id}'
        
        # Join private chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark user as online for this private chat
        await self.mark_user_online()
        
        # Notify other user that this user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'status': 'Online',
                'user': self.scope['user'].username
            }
        )
    
    async def disconnect(self, close_code):
        # Mark user as offline
        await self.mark_user_offline()
        
        # Notify other user that this user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'status': 'Offline',
                'user': self.scope['user'].username
            }
        )
        
        # Leave private chat group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                message = data.get('message', '').strip()
                receiver_id = data.get('receiver_id')
                
                if message and receiver_id:
                    # Save message to database
                    await self.save_message(message, receiver_id)
                    
                    # Send message to private chat group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'sender': self.scope['user'].username,
                            'timestamp': json.dumps(timezone.now(), default=str)
                        }
                    )
                    
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in PrivateChatConsumer")
        except Exception as e:
            logger.error(f"Error in PrivateChatConsumer receive: {e}")
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))
    
    async def user_status(self, event):
        """Send user status to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'status': event['status'],
            'user': event['user']
        }))
    
    @database_sync_to_async
    def save_message(self, message, receiver_id):
        """Save private message to database"""
        try:
            from django.contrib.auth.models import User
            from .models import PrivateChat, PrivateMessage
            from django.utils import timezone
            
            receiver = User.objects.get(id=receiver_id)
            chat, created = PrivateChat.get_or_create_chat(self.scope['user'], receiver)
            
            # Create the message
            PrivateMessage.objects.create(
                chat=chat,
                sender=self.scope['user'],
                content=message,
                timestamp=timezone.now()
            )
            
        except Exception as e:
            logger.error(f"Error saving private message: {e}")
    
    @database_sync_to_async
    def mark_user_online(self):
        """Mark user as online for this private chat"""
        try:
            from django.core.cache import cache
            import time
            
            user_online_key = f"private_chat_{self.chat_id}_user_{self.scope['user'].id}_online"
            cache.set(user_online_key, time.time(), timeout=300)  # 5 minutes
            
        except Exception as e:
            logger.error(f"Error marking user online for private chat: {e}")
    
    @database_sync_to_async
    def mark_user_offline(self):
        """Mark user as offline for this private chat"""
        try:
            from django.core.cache import cache
            
            user_online_key = f"private_chat_{self.chat_id}_user_{self.scope['user'].id}_online"
            cache.delete(user_online_key)
            
        except Exception as e:
            logger.error(f"Error marking user offline for private chat: {e}")