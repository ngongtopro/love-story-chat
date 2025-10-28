from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime


def send_realtime_update(event_type: str, data: dict, user_id=None, broadcast=False):
    """
    Send realtime update through channels
    
    Args:
        event_type: Type of event (e.g., 'wallet_updated', 'caro_room_created')
        data: Event data dictionary
        user_id: If provided, send only to this user. If None and broadcast=False, send to global
        broadcast: If True, send to all connected users
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        print("⚠️ Channel layer not configured")
        return
    
    message = {
        'type': event_type.replace('.', '_'),  # Convert dots to underscores for channel method names
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        if user_id:
            # Send to specific user
            group_name = f'user_{user_id}'
            async_to_sync(channel_layer.group_send)(group_name, message)
            print(f"📤 Sent {event_type} to user {user_id}")
        elif broadcast:
            # Send to all users
            group_name = 'global_updates'
            async_to_sync(channel_layer.group_send)(group_name, message)
            print(f"📤 Broadcast {event_type} to all users")
        else:
            # Send to global group (default)
            group_name = 'global_updates'
            async_to_sync(channel_layer.group_send)(group_name, message)
            print(f"📤 Sent {event_type} to global group")
    except Exception as e:
        print(f"❌ Error sending realtime update: {e}")


def notify_wallet_updated(user_id: int, balance: float, transaction=None):
    """Notify user that their wallet was updated"""
    data = {
        'balance': balance,
    }
    if transaction:
        data['transaction'] = {
            'id': transaction.id,
            'amount': float(transaction.amount),
            'transaction_type': transaction.transaction_type,
            'description': transaction.description,
            'created_at': transaction.created_at.isoformat(),
        }
    
    send_realtime_update('wallet.updated', data, user_id=user_id)


def notify_wallet_transaction(user_id: int, transaction):
    """Notify user of a new transaction"""
    data = {
        'id': transaction.id,
        'amount': float(transaction.amount),
        'transaction_type': transaction.transaction_type,
        'description': transaction.description,
        'balance_after': float(transaction.balance_after) if transaction.balance_after else None,
        'created_at': transaction.created_at.isoformat(),
    }
    
    send_realtime_update('wallet.transaction', data, user_id=user_id)


def notify_caro_room_created(room):
    """Notify all users that a new Caro room was created"""
    from caro_game.serializers import CaroGameSerializer
    
    data = CaroGameSerializer(room).data
    send_realtime_update('caro.room_created', data, broadcast=True)


def notify_caro_room_updated(room):
    """Notify all users that a Caro room was updated"""
    from caro_game.serializers import CaroGameSerializer
    
    data = CaroGameSerializer(room).data
    send_realtime_update('caro.room_updated', data, broadcast=True)


def notify_caro_room_deleted(room_id: int, room_name: str):
    """Notify all users that a Caro room was deleted"""
    data = {
        'id': room_id,
        'room_name': room_name
    }
    send_realtime_update('caro.room_deleted', data, broadcast=True)


def notify_caro_game_started(room):
    """Notify players that game started"""
    from caro_game.serializers import CaroGameSerializer
    
    data = CaroGameSerializer(room).data
    
    # Send to both players
    if room.player1:
        send_realtime_update('caro.game_started', data, user_id=room.player1.id)
    if room.player2:
        send_realtime_update('caro.game_started', data, user_id=room.player2.id)


def notify_caro_game_move(room, move):
    """Notify players of a new move"""
    from caro_game.serializers import CaroGameSerializer
    
    data = {
        'room': CaroGameSerializer(room).data,
        'move': {
            'row': move.row,
            'col': move.col,
            'player': move.player.username if move.player else None,
        }
    }
    
    # Send to both players
    if room.player1:
        send_realtime_update('caro.game_move', data, user_id=room.player1.id)
    if room.player2:
        send_realtime_update('caro.game_move', data, user_id=room.player2.id)


def notify_caro_game_ended(room, winner=None):
    """Notify players that game ended"""
    from caro_game.serializers import CaroGameSerializer
    
    data = {
        'room': CaroGameSerializer(room).data,
        'winner': winner.username if winner else None,
    }
    
    # Send to both players
    if room.player1:
        send_realtime_update('caro.game_ended', data, user_id=room.player1.id)
    if room.player2:
        send_realtime_update('caro.game_ended', data, user_id=room.player2.id)


def notify_chat_new_message(message_obj):
    """Notify room members of new message"""
    data = {
        'id': message_obj.id,
        'room_id': message_obj.room.id,
        'sender': message_obj.sender.username if message_obj.sender else None,
        'content': message_obj.content,
        'created_at': message_obj.created_at.isoformat(),
    }
    
    # Send to all room members
    # You'll need to implement logic to get room members
    send_realtime_update('chat.new_message', data, broadcast=True)


def notify_general(user_id: int, message: str, level='info'):
    """Send a general notification to user"""
    data = {
        'message': message,
        'level': level,  # 'info', 'success', 'warning', 'error'
    }
    
    send_realtime_update('notification.new', data, user_id=user_id)
