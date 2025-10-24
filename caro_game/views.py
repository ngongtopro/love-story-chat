from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from .models import CaroGame, CaroMove
from chat.models import PrivateChat
import json
import logging

logger = logging.getLogger(__name__)


# ===========================
# PRIVATE CHAT CARO GAME VIEWS
# ===========================

@login_required
@csrf_exempt
def create_private_caro_game(request, user_id):
    """Create a new Caro game in private chat"""
    if request.method == 'POST':
        try:
            other_user = get_object_or_404(User, id=user_id)
            chat, _ = PrivateChat.get_or_create_chat(request.user, other_user)
            
            # Check if there's already an active game
            active_game = CaroGame.get_active_game(chat_id=chat.chat_id)
            if active_game:
                return JsonResponse({
                    'error': 'There is already an active game in this chat',
                    'game': active_game.to_dict()
                })
            
            # Create new game
            game = CaroGame.create_game(request.user, chat.chat_id)
            if game:
                return JsonResponse({
                    'success': True,
                    'game': game.to_dict()
                })
            else:
                return JsonResponse({'error': 'Failed to create game'}, status=500)
                
        except Exception as e:
            logger.error(f"Error creating private Caro game: {e}")
            return JsonResponse({'error': 'Failed to create game'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
@csrf_exempt
def join_private_caro_game(request, user_id):
    """Join an existing Caro game in private chat"""
    if request.method == 'POST':
        try:
            other_user = get_object_or_404(User, id=user_id)
            chat, _ = PrivateChat.get_or_create_chat(request.user, other_user)
            
            active_game = CaroGame.get_active_game(chat_id=chat.chat_id)
            if not active_game:
                return JsonResponse({'error': 'No active game found'}, status=404)
            
            if active_game.status != 'waiting':
                return JsonResponse({'error': 'Game is not waiting for players'})
            
            if active_game.player1 == request.user:
                return JsonResponse({'error': 'You cannot join your own game'})
            
            # Join the game
            if active_game.join_game(request.user):
                return JsonResponse({
                    'success': True,
                    'game': active_game.to_dict()
                })
            else:
                return JsonResponse({'error': 'Failed to join game'}, status=500)
                
        except Exception as e:
            logger.error(f"Error joining private Caro game: {e}")
            return JsonResponse({'error': 'Failed to join game'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
@csrf_exempt
def make_private_caro_move(request, user_id):
    """Make a move in private chat Caro game"""
    if request.method == 'POST':
        try:
            other_user = get_object_or_404(User, id=user_id)
            chat, _ = PrivateChat.get_or_create_chat(request.user, other_user)
            
            data = json.loads(request.body)
            row = data.get('row')
            col = data.get('col')
            game_id = data.get('game_id')
            
            if row is None or col is None or not game_id:
                return JsonResponse({'error': 'Missing required parameters'}, status=400)
            
            # Get game
            game = get_object_or_404(CaroGame, id=game_id, chat_id=chat.chat_id)
            
            # Make move
            success, message = game.make_game_move(row, col, request.user)
            if success:
                return JsonResponse({
                    'success': True,
                    'game': game.to_dict()
                })
            else:
                return JsonResponse({'error': message}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error making private Caro move: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def get_private_caro_game(request, user_id):
    """Get current private chat Caro game status"""
    try:
        other_user = get_object_or_404(User, id=user_id)
        chat, _ = PrivateChat.get_or_create_chat(request.user, other_user)
        
        active_game = CaroGame.get_active_game(chat_id=chat.chat_id)
        if active_game:
            return JsonResponse({
                'success': True,
                'game': active_game.to_dict()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No active game'
            })
    except Exception as e:
        logger.error(f"Error getting private Caro game: {e}")
        return JsonResponse({'error': 'Failed to get game status'}, status=500)


@login_required
@csrf_exempt
def abandon_private_caro_game(request, user_id):
    """Abandon current private chat Caro game"""
    if request.method == 'POST':
        try:
            other_user = get_object_or_404(User, id=user_id)
            chat, _ = PrivateChat.get_or_create_chat(request.user, other_user)
            
            active_game = CaroGame.get_active_game(chat_id=chat.chat_id)
            if not active_game:
                return JsonResponse({'error': 'No active game found'}, status=404)
            
            # Check if user is part of the game
            if (active_game.player1 != request.user and 
                (not active_game.player2 or active_game.player2 != request.user)):
                return JsonResponse({'error': 'You are not part of this game'}, status=403)
            
            # Abandon the game
            if active_game.abandon_game(request.user):
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Failed to abandon game'}, status=500)
            
        except Exception as e:
            logger.error(f"Error abandoning private Caro game: {e}")
            return JsonResponse({'error': 'Failed to abandon game'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# ===========================
# ROOM CARO GAME VIEWS (Legacy support)
# ===========================

@login_required
@csrf_exempt
def create_room_caro_game(request, room_name=None):
    """Create a new Caro game room - Show form and handle room creation"""
    # Detect if this is an API call (room_name provided in URL)
    is_api_call = room_name is not None
    
    if request.method == 'POST':
        # If room_name is passed as URL parameter, use it; otherwise get from POST data
        if room_name is None:
            room_name = request.POST.get('room_name')
        room_description = request.POST.get('room_description', '')
        
        if not room_name:
            if is_api_call:
                return JsonResponse({'error': 'Room name is required!'}, status=400)
            return render(request, 'caro_game/create_room.html', {
                'error': 'Room name is required!'
            })
        
        # Validate room name
        room_name = room_name.strip()
        if len(room_name) < 3:
            error_msg = 'Room name must be at least 3 characters long!'
            if is_api_call:
                return JsonResponse({'error': error_msg}, status=400)
            return render(request, 'caro_game/create_room.html', {
                'error': error_msg
            })
        
        if len(room_name) > 50:
            error_msg = 'Room name must be less than 50 characters!'
            if is_api_call:
                return JsonResponse({'error': error_msg}, status=400)
            return render(request, 'caro_game/create_room.html', {
                'error': error_msg
            })
        
        try:
            # Use local models for room-based games
            from . import models as caro_models
            
            # The active game checking is now handled in create_game function
            
            # Create new game using caro_models
            game_data = caro_models.create_game(room_name, request.user.username)
            if game_data and 'error' not in game_data:
                if is_api_call:
                    return JsonResponse({
                        'success': True,
                        'room_name': room_name,
                        'game': game_data
                    })
                else:
                    # Redirect to the game room
                    from django.shortcuts import redirect
                    return redirect('caro_game:caro_game_room', room_name=room_name)
            else:
                # Handle different error types
                if game_data and 'error' in game_data:
                    error_type = game_data.get('error')
                    error_msg = game_data.get('message', 'Failed to create game')
                    
                    if error_type in ['game_in_progress', 'game_waiting']:
                        status_code = 400
                    elif error_type in ['insufficient_balance', 'no_wallet']:
                        status_code = 402  # Payment Required
                    else:
                        status_code = 500
                    
                    if is_api_call:
                        # Enhanced response for game_waiting error
                        if error_type == 'game_waiting':
                            existing_game = game_data.get('existing_game', {})
                            response_data = {
                                'error': 'game_waiting',
                                'message': f'Room "{room_name}" has a game waiting for players',
                                'action_required': 'join_existing_game',
                                'existing_game': {
                                    'id': existing_game.get('id'),
                                    'player1': existing_game.get('player1'),
                                    'created_at': existing_game.get('created_at'),
                                    'bet_amount': existing_game.get('bet_amount', 10000)
                                },
                                'join_url': f'/api/caro/{room_name}/join/',
                                'instructions': {
                                    'method': 'POST',
                                    'endpoint': f'/api/caro/{room_name}/join/',
                                    'description': 'Make a POST request to this endpoint to join the waiting game'
                                }
                            }
                            return JsonResponse(response_data, status=status_code)
                        return JsonResponse(game_data, status=status_code)
                    return render(request, 'caro_game/create_room.html', {
                        'error': error_msg,
                        'existing_game': game_data.get('existing_game')
                    })
                else:
                    error_msg = 'Failed to create game. Please try again.'
                    if is_api_call:
                        return JsonResponse({'error': error_msg}, status=500)
                    return render(request, 'caro_game/create_room.html', {
                        'error': error_msg
                    })
                
        except Exception as e:
            logger.error(f"Error creating Caro game: {e}")
            error_msg = 'An error occurred while creating the room. Please try again.'
            if is_api_call:
                return JsonResponse({'error': error_msg}, status=500)
            return render(request, 'caro_game/create_room.html', {
                'error': error_msg
            })
    
    # GET request
    if is_api_call:
        return JsonResponse({'error': 'Only POST method is allowed for API calls'}, status=405)
    return render(request, 'caro_game/create_room.html')


@login_required
@csrf_exempt
def join_room_caro_game(request, room_name):
    """Join an existing Caro game room"""
    if request.method == 'POST':
        try:
            # Use caro_models for room-based games
            from . import models as caro_models
            
            active_game = caro_models.get_active_game(room_name)
            if not active_game:
                return JsonResponse({'error': 'No active game found'}, status=404)
            
            if active_game.get('status') != 'waiting':
                return JsonResponse({'error': 'Game is not waiting for players'})
            
            if active_game.get('player1') == request.user.username:
                return JsonResponse({'error': 'You cannot join your own game'})
            
            # Join the game
            result = caro_models.join_game(room_name, request.user.username)
            if result:
                # Get updated game data
                updated_game = caro_models.get_active_game(room_name)
                return JsonResponse({
                    'success': True,
                    'game': updated_game
                })
            else:
                return JsonResponse({'error': 'Failed to join game'}, status=500)
                
        except Exception as e:
            logger.error(f"Error joining Caro game: {e}")
            return JsonResponse({'error': 'Failed to join game'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
@csrf_exempt
def make_room_caro_move(request, room_name):
    """Make a move in Caro game - Legacy support"""
    if request.method == 'POST':
        try:
            # Use caro_models for room-based games
            from . import models as caro_models
            
            data = json.loads(request.body)
            row = data.get('row')
            col = data.get('col')
            
            if row is None or col is None:
                return JsonResponse({'error': 'Missing row or col'}, status=400)
            
            # Make move using caro_models
            # First get the active game to get game_id
            active_game = caro_models.get_active_game(room_name)
            if not active_game:
                return JsonResponse({'error': 'No active game found'}, status=404)
            
            game_id = active_game.get('id') or active_game.get('_id')
            result = caro_models.make_move(str(game_id), row, col, request.user.username)
            if result:
                return JsonResponse({
                    'success': True,
                    'game': result
                })
            else:
                return JsonResponse({'error': 'Invalid move'}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error making Caro move: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def get_room_caro_game(request, room_name):
    """Get current Caro game status - Legacy support"""
    try:
        # Use caro_models for room-based games  
        from . import models as caro_models
        
        active_game = caro_models.get_active_game(room_name)
        if active_game:
            return JsonResponse({
                'success': True,
                'game': active_game
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No active game'
            })
    except Exception as e:
        logger.error(f"Error getting Caro game: {e}")
        return JsonResponse({'error': 'Failed to get game status'}, status=500)


@login_required
@csrf_exempt
def abandon_room_caro_game(request, room_name):
    """Abandon current Caro game - Legacy support"""
    if request.method == 'POST':
        try:
            # Use caro_models for room-based games
            from . import models as caro_models
            
            active_game = caro_models.get_active_game(room_name)
            if not active_game:
                return JsonResponse({'error': 'No active game found'}, status=404)
            
            # Check if user is part of the game
            player1 = active_game.get('player1')
            player2 = active_game.get('player2')
            if (player1 != request.user.username and 
                (not player2 or player2 != request.user.username)):
                return JsonResponse({'error': 'You are not part of this game'}, status=403)
            
            # Abandon the game using caro_models
            result = caro_models.abandon_game(room_name, request.user.username)
            if result:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Failed to abandon game'}, status=500)
            
        except Exception as e:
            logger.error(f"Error abandoning Caro game: {e}")
            return JsonResponse({'error': 'Failed to abandon game'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# ===========================
# GAME STATISTICS VIEWS
# ===========================

@login_required
def get_game_stats(request):
    """Get user's Caro game statistics"""
    try:
        # Get all game stats (all are room games now)
        total_games_won = CaroGame.objects.filter(winner=request.user).count()
        total_games_played = CaroGame.objects.filter(
            Q(player1=request.user) | Q(player2=request.user),
            status='finished'
        ).count()
        
        win_rate = (total_games_won / total_games_played * 100) if total_games_played > 0 else 0
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_games_played': total_games_played,
                'total_games_won': total_games_won,
                'win_rate': round(win_rate, 1)
            }
        })
    except Exception as e:
        logger.error(f"Error getting game stats: {e}")
        return JsonResponse({'error': 'Failed to get stats'}, status=500)


@login_required
def caro_game_room(request, room_name):
    """Display the Caro game room interface"""
    try:
        # Use local models for room-based games
        from . import models as caro_models
        
        # Get or create room data
        active_game = caro_models.get_active_game(room_name)
        
        # If no game exists, create one
        if not active_game:
            game_data = caro_models.create_game(room_name, request.user.username)
            if not game_data:
                return render(request, 'caro_game/create_room.html', {
                    'error': f'Failed to create game room "{room_name}". Please try again.'
                })
            active_game = game_data
        
        # Check if user can access this room
        current_username = request.user.username
        player1 = active_game.get('player1')
        player2 = active_game.get('player2')
        
        # Allow room creator, second player, or if room is waiting for players
        can_access = (
            current_username == player1 or 
            current_username == player2 or 
            active_game.get('status') == 'waiting'
        )
        
        if not can_access:
            return render(request, 'caro_game/create_room.html', {
                'error': f'Room "{room_name}" is full or you do not have access to this room.'
            })
        
        # Prepare context for the template
        context = {
            'room': {
                'name': room_name,
                'description': f'Caro Game Room: {room_name}'
            },
            'room_name': room_name,
            'game_data': active_game,
            'current_user': request.user.username,
            'is_player1': current_username == player1,
            'is_player2': current_username == player2,
            'can_play': current_username in [player1, player2] if player2 else current_username == player1
        }
        
        return render(request, 'caro_game/game_base.html', context)
        
    except Exception as e:
        logger.error(f"Error accessing Caro game room {room_name}: {e}")
        return render(request, 'caro_game/create_room.html', {
            'error': f'An error occurred while accessing room "{room_name}". Please try again.'
        })


@login_required
def list_caro_rooms(request):
    """List all available Caro game rooms"""
    try:
        # Get all active games
        from . import models as caro_models
        
        # Get waiting rooms (where players can join)
        waiting_rooms = CaroGame.objects.filter(
            status='waiting'
        ).select_related('player1').order_by('-created_at')
        
        # Get playing rooms (for viewing)
        playing_rooms = CaroGame.objects.filter(
            status='playing'
        ).select_related('player1', 'player2').order_by('-updated_at')[:10]
        
        context = {
            'waiting_rooms': waiting_rooms,
            'playing_rooms': playing_rooms,
            'current_user': request.user.username
        }
        
        return render(request, 'caro_game/room_list.html', context)
        
    except Exception as e:
        logger.error(f"Error listing Caro rooms: {e}")
        return render(request, 'caro_game/room_list.html', {
            'error': 'An error occurred while loading rooms. Please try again.',
            'waiting_rooms': [],
            'playing_rooms': []
        })


# ===========================
# API ENDPOINTS
# ===========================

def api_test(request):
    """Simple API test endpoint"""
    return JsonResponse({
        'success': True,
        'message': 'API test endpoint working',
        'method': request.method,
        'path': request.path
    })

def get_room_game_status(request, room_name):
    """Get current game status for a room"""
    # Add immediate debug output
    print(f"DEBUG: get_room_game_status called with room_name={room_name}")
    logger.info(f"DEBUG: get_room_game_status called with room_name={room_name}")
    
    # Return simple JSON for now to test
    return JsonResponse({
        'success': True,
        'message': f'API called for room: {room_name}',
        'game': None
    })
    
    try:
        logger.info(f"Getting room game status for: {room_name}")
        
        # Check if CaroGame model exists and is accessible
        try:
            room_game = CaroGame.objects.filter(
                room_name=room_name,
                status__in=['waiting', 'playing']
            ).first()
            
            logger.info(f"Query executed, found game: {room_game is not None}")
            
        except Exception as db_error:
            logger.error(f"Database query error for room {room_name}: {db_error}")
            # Return success with no game instead of error
            return JsonResponse({
                'success': True,
                'game': None,
                'message': 'No active game found'
            })
        
        if room_game:
            try:
                # Safely access model attributes with proper error handling
                game_data = {
                    'id': getattr(room_game, 'id', None),
                    'room_name': getattr(room_game, 'room_name', room_name),
                    'status': getattr(room_game, 'status', 'unknown'),
                    'player1': None,
                    'player2': None,
                    'current_player': None,
                    'board': getattr(room_game, 'board_state', ''),
                    'winner': None,
                    'created_at': None,
                    'updated_at': None
                }
                
                # Safely get player1 username
                try:
                    if hasattr(room_game, 'player1') and room_game.player1:
                        game_data['player1'] = room_game.player1.username
                except:
                    pass
                
                # Safely get player2 username  
                try:
                    if hasattr(room_game, 'player2') and room_game.player2:
                        game_data['player2'] = room_game.player2.username
                except:
                    pass
                
                # Safely get current_turn (X or O)
                try:
                    if hasattr(room_game, 'current_turn') and room_game.current_turn:
                        game_data['current_player'] = room_game.current_turn
                except:
                    pass
                
                # Safely get winner username
                try:
                    if hasattr(room_game, 'winner') and room_game.winner:
                        game_data['winner'] = room_game.winner.username
                except:
                    pass
                
                # Safely get timestamps
                try:
                    if hasattr(room_game, 'created_at') and room_game.created_at:
                        game_data['created_at'] = room_game.created_at.isoformat()
                except:
                    pass
                
                try:
                    if hasattr(room_game, 'updated_at') and room_game.updated_at:
                        game_data['updated_at'] = room_game.updated_at.isoformat()
                except:
                    pass
                
                return JsonResponse({
                    'success': True,
                    'game': game_data
                })
                
            except Exception as attr_error:
                logger.error(f"Error accessing model attributes: {attr_error}")
                return JsonResponse({
                    'success': True,
                    'game': None,
                    'message': f'Error reading game data: {str(attr_error)}'
                })
        else:
            # No active game in this room
            logger.info(f"No active game found for room: {room_name}")
            return JsonResponse({
                'success': True,
                'game': None,
                'message': 'No active game in this room'
            })
            
    except Exception as e:
        logger.error(f"Unexpected error in get_room_game_status for {room_name}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)
