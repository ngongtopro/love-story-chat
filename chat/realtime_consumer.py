import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class RealtimeConsumer(AsyncWebsocketConsumer):
    """
    Global realtime consumer for all app updates
    Only updates what changes, not full reloads
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user', AnonymousUser())
        
        # If anonymous, try to get token from query params
        if self.user.is_anonymous:
            query_string = self.scope.get('query_string', b'').decode()
            if 'token=' in query_string:
                from urllib.parse import parse_qs
                params = parse_qs(query_string)
                token = params.get('token', [None])[0]
                
                if token:
                    # Try to authenticate with token
                    from rest_framework_simplejwt.tokens import AccessToken
                    from django.contrib.auth import get_user_model
                    try:
                        access_token = AccessToken(token)
                        user_id = access_token['user_id']
                        User = get_user_model()
                        self.user = await self.get_user(user_id)
                    except Exception as e:
                        print(f"❌ Token authentication failed: {e}")
        
        if self.user.is_anonymous:
            print("❌ Anonymous user tried to connect to realtime")
            await self.close()
            return

        self.user_id = str(self.user.id)
        
        # Join user-specific group for personal updates
        self.user_group = f'user_{self.user_id}'
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        
        # Join global updates group
        self.global_group = 'global_updates'
        await self.channel_layer.group_add(self.global_group, self.channel_name)
        
        await self.accept()
        print(f"✅ Realtime connected: {self.user.username}")
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from database"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if hasattr(self, 'global_group'):
            await self.channel_layer.group_discard(self.global_group, self.channel_name)
        
        print(f"🔌 Realtime disconnected: {getattr(self, 'user', 'unknown')}")

    async def receive(self, text_data):
        """Handle incoming messages from WebSocket"""
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            
            # Handle different event types if needed
            print(f"📨 Received from {self.user.username}: {event_type}")
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON received")
        except Exception as e:
            print(f"❌ Error in receive: {e}")

    # Event handlers for different update types
    
    async def wallet_updated(self, event):
        """Send wallet balance update"""
        await self.send(text_data=json.dumps({
            'type': 'wallet.updated',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def wallet_transaction(self, event):
        """Send new transaction notification"""
        await self.send(text_data=json.dumps({
            'type': 'wallet.transaction',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def caro_room_created(self, event):
        """Send room created notification"""
        await self.send(text_data=json.dumps({
            'type': 'caro.room_created',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def caro_room_updated(self, event):
        """Send room updated notification"""
        await self.send(text_data=json.dumps({
            'type': 'caro.room_updated',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def caro_room_deleted(self, event):
        """Send room deleted notification"""
        await self.send(text_data=json.dumps({
            'type': 'caro.room_deleted',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def caro_game_started(self, event):
        """Send game started notification"""
        await self.send(text_data=json.dumps({
            'type': 'caro.game_started',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def caro_game_move(self, event):
        """Send game move notification"""
        await self.send(text_data=json.dumps({
            'type': 'caro.game_move',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def caro_game_ended(self, event):
        """Send game ended notification"""
        await self.send(text_data=json.dumps({
            'type': 'caro.game_ended',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def chat_new_message(self, event):
        """Send new chat message notification"""
        await self.send(text_data=json.dumps({
            'type': 'chat.new_message',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def chat_room_updated(self, event):
        """Send chat room update notification"""
        await self.send(text_data=json.dumps({
            'type': 'chat.room_updated',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def farm_crop_ready(self, event):
        """Send crop ready notification"""
        await self.send(text_data=json.dumps({
            'type': 'farm.crop_ready',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def farm_animal_ready(self, event):
        """Send animal ready notification"""
        await self.send(text_data=json.dumps({
            'type': 'farm.animal_ready',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))

    async def notification_new(self, event):
        """Send general notification"""
        await self.send(text_data=json.dumps({
            'type': 'notification.new',
            'data': event['data'],
            'timestamp': event.get('timestamp')
        }))
