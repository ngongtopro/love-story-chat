from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import CaroGame, CaroMove
import json
import logging

logger = logging.getLogger(__name__)


class CaroRoomListConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Caro room list real-time updates"""
    
    async def connect(self):
        self.room_group_name = 'caro_room_list'
        
        # Join caro room list group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info("✅ CaroRoomListConsumer connected")
        
        # Send current rooms list on connect
        try:
            rooms_data = await self.get_rooms_list()
            await self.send(text_data=json.dumps({
                'type': 'rooms_update',
                'data': rooms_data
            }))
            logger.info(f"📤 Sent initial rooms data: {len(rooms_data.get('waiting', []))} waiting, {len(rooms_data.get('playing', []))} playing")
        except Exception as e:
            logger.error(f"❌ Error sending initial rooms data: {str(e)}", exc_info=True)
            # Don't close the connection, just send empty data
            await self.send(text_data=json.dumps({
                'type': 'rooms_update',
                'data': {'waiting': [], 'playing': []}
            }))
    
    async def disconnect(self, close_code):
        # Leave caro room list group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'refresh_rooms':
                # Client requests room list refresh
                rooms_data = await self.get_rooms_list()
                await self.send(text_data=json.dumps({
                    'type': 'rooms_update',
                    'data': rooms_data
                }))
        except Exception as e:
            logger.error(f"Error in CaroRoomListConsumer.receive: {str(e)}")
    
    async def rooms_update(self, event):
        """Receive rooms_update from group and send to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'rooms_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_rooms_list(self):
        """Get list of waiting and playing rooms"""
        user = self.scope.get('user')
        
        # Get waiting rooms (exclude user's own games if authenticated)
        waiting_query = CaroGame.objects.filter(status='waiting').order_by('-created_at')
        if user and user.is_authenticated:
            waiting_query = waiting_query.exclude(player1=user)
        
        waiting_games = waiting_query[:20]  # Limit to 20
        
        # Get playing rooms
        playing_games = CaroGame.objects.filter(
            status='playing'
        ).order_by('-updated_at')[:20]  # Limit to 20
        
        waiting_data = [{
            'id': game.id,
            'game_id': game.game_id,
            'room_name': game.room_name,
            'player1': game.player1.username,
            'player2': game.player2.username if game.player2 else None,
            'status': game.status,
            'bet_amount': game.bet_amount,
            'created_at': game.created_at.isoformat(),
        } for game in waiting_games]
        
        playing_data = [{
            'id': game.id,
            'game_id': game.game_id,
            'room_name': game.room_name,
            'player1': game.player1.username,
            'player2': game.player2.username if game.player2 else None,
            'status': game.status,
            'bet_amount': game.bet_amount,
            'created_at': game.created_at.isoformat(),
        } for game in playing_games]
        
        return {
            'waiting': waiting_data,
            'playing': playing_data
        }


class CaroGameConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for individual Caro game real-time updates"""
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'caro_game_{self.room_name}'
        
        # Join game room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current game state on connect
        game_data = await self.get_game_state()
        if game_data:
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'data': game_data
            }))
    
    async def disconnect(self, close_code):
        # Leave game room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'make_move':
                # Handle move request
                row = data.get('row')
                col = data.get('col')
                
                result = await self.handle_move(row, col)
                
                if result['success']:
                    # Broadcast move to all players in game room
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_state',
                            'data': result['game_data']
                        }
                    )
                    
                    # Also notify room list that game state changed
                    await self.notify_room_list_update()
                else:
                    # Send error only to this player
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': result['message']
                    }))
            
            elif message_type == 'refresh_game':
                # Client requests game state refresh
                game_data = await self.get_game_state()
                if game_data:
                    await self.send(text_data=json.dumps({
                        'type': 'game_state',
                        'data': game_data
                    }))
        
        except Exception as e:
            logger.error(f"Error in CaroGameConsumer.receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid request'
            }))
    
    async def game_state(self, event):
        """Receive game_state from group and send to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_game_state(self):
        """Get current game state"""
        try:
            game = CaroGame.objects.get(room_name=self.room_name)
            
            # Get all moves
            moves = game.moves.all().order_by('move_number')
            moves_data = [{
                'row': move.row,
                'col': move.col,
                'symbol': move.symbol,
                'move_number': move.move_number,
                'player_username': move.player.username,
                'timestamp': move.timestamp.isoformat(),
            } for move in moves]
            
            return {
                'id': game.id,
                'game_id': game.game_id,
                'room_name': game.room_name,
                'player1': {
                    'username': game.player1.username,
                    'display_name': game.player1.first_name or game.player1.username,
                },
                'player2': {
                    'username': game.player2.username,
                    'display_name': game.player2.first_name or game.player2.username,
                } if game.player2 else None,
                'current_turn': game.current_turn,
                'status': game.status,
                'winner': {
                    'username': game.winner.username,
                    'display_name': game.winner.first_name or game.winner.username,
                } if game.winner else None,
                'total_moves': game.total_moves,
                'moves': moves_data,
                'bet_amount': game.bet_amount,
                'total_pot': game.total_pot,
                'winner_prize': game.winner_prize,
                'house_fee': game.house_fee,
            }
        except CaroGame.DoesNotExist:
            return None
    
    @database_sync_to_async
    def handle_move(self, row, col):
        """Handle player move"""
        try:
            user = self.scope.get('user')
            if not user or not user.is_authenticated:
                return {'success': False, 'message': 'Not authenticated'}
            
            game = CaroGame.objects.get(room_name=self.room_name)
            
            # Validate it's player's turn
            if game.current_turn == 'X' and user != game.player1:
                return {'success': False, 'message': 'Not your turn'}
            if game.current_turn == 'O' and user != game.player2:
                return {'success': False, 'message': 'Not your turn'}
            
            # Make the move
            result = game.make_game_move(user, row, col)
            
            # Get updated game state
            moves = game.moves.all().order_by('move_number')
            moves_data = [{
                'row': move.row,
                'col': move.col,
                'symbol': move.symbol,
                'move_number': move.move_number,
                'player_username': move.player.username,
                'timestamp': move.timestamp.isoformat(),
            } for move in moves]
            
            game_data = {
                'id': game.id,
                'game_id': game.game_id,
                'room_name': game.room_name,
                'player1': {
                    'username': game.player1.username,
                    'display_name': game.player1.first_name or game.player1.username,
                },
                'player2': {
                    'username': game.player2.username,
                    'display_name': game.player2.first_name or game.player2.username,
                } if game.player2 else None,
                'current_turn': game.current_turn,
                'status': game.status,
                'winner': {
                    'username': game.winner.username,
                    'display_name': game.winner.first_name or game.winner.username,
                } if game.winner else None,
                'total_moves': game.total_moves,
                'moves': moves_data,
                'bet_amount': game.bet_amount,
                'total_pot': game.total_pot,
                'winner_prize': game.winner_prize,
                'house_fee': game.house_fee,
            }
            
            return {
                'success': True,
                'message': result['message'],
                'game_data': game_data
            }
            
        except CaroGame.DoesNotExist:
            return {'success': False, 'message': 'Game not found'}
        except Exception as e:
            logger.error(f"Error in handle_move: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def notify_room_list_update(self):
        """Notify room list consumers that rooms have updated"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        # Get updated rooms list
        rooms_data = await self.get_rooms_list()
        
        # Broadcast to room list group
        await channel_layer.group_send(
            'caro_room_list',
            {
                'type': 'rooms_update',
                'data': rooms_data
            }
        )
    
    @database_sync_to_async
    def get_rooms_list(self):
        """Get list of waiting and playing rooms"""
        # Get waiting rooms
        waiting_games = CaroGame.objects.filter(
            status='waiting'
        ).order_by('-created_at')[:20]
        
        # Get playing rooms
        playing_games = CaroGame.objects.filter(
            status='playing'
        ).order_by('-updated_at')[:20]
        
        waiting_data = [{
            'id': game.id,
            'game_id': game.game_id,
            'room_name': game.room_name,
            'player1': game.player1.username,
            'player2': game.player2.username if game.player2 else None,
            'status': game.status,
            'bet_amount': game.bet_amount,
            'created_at': game.created_at.isoformat(),
        } for game in waiting_games]
        
        playing_data = [{
            'id': game.id,
            'game_id': game.game_id,
            'room_name': game.room_name,
            'player1': game.player1.username,
            'player2': game.player2.username if game.player2 else None,
            'status': game.status,
            'bet_amount': game.bet_amount,
            'created_at': game.created_at.isoformat(),
        } for game in playing_games]
        
        return {
            'waiting': waiting_data,
            'playing': playing_data
        }
