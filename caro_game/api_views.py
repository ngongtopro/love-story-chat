from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Count, Case, When, IntegerField
from drf_yasg.utils import swagger_auto_schema

from .models import CaroGame
from .serializers import (
    CaroGameSerializer, CaroGameCreateSerializer, 
    CaroMoveSerializer, CaroGameStatsSerializer
)


class CaroGameViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Caro games
    """
    serializer_class = CaroGameSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'player1', 'player2']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Get games for current user"""
        user = self.request.user
        return CaroGame.objects.filter(
            Q(player1=user) | Q(player2=user)
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return CaroGameCreateSerializer
        return CaroGameSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def make_move(self, request, pk=None):
        """Make a move in the game"""
        game = self.get_object()
        serializer = CaroMoveSerializer(data=request.data, context={'request': request, 'game': game})
        serializer.is_valid(raise_exception=True)
        
        row = serializer.validated_data['row']
        col = serializer.validated_data['col']
        
        try:
            result = game.make_move(request.user, row, col)
            game_serializer = self.get_serializer(game)
            
            return Response({
                'game': game_serializer.data,
                'move_result': result
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def join_game(self, request, pk=None):
        """Join a waiting game"""
        game = self.get_object()
        
        if game.status != 'waiting':
            return Response({'error': 'Game is not waiting for players'}, status=status.HTTP_400_BAD_REQUEST)
        
        if game.player1 == request.user:
            return Response({'error': 'Cannot join your own game'}, status=status.HTTP_400_BAD_REQUEST)
        
        if game.player2 is not None:
            return Response({'error': 'Game is already full'}, status=status.HTTP_400_BAD_REQUEST)
        
        game.player2 = request.user
        game.status = 'playing'
        game.save()
        
        serializer = self.get_serializer(game)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def abandon_game(self, request, pk=None):
        """Abandon the game"""
        game = self.get_object()
        
        if request.user not in [game.player1, game.player2]:
            return Response({'error': 'Not a player in this game'}, status=status.HTTP_403_FORBIDDEN)
        
        if game.status == 'finished':
            return Response({'error': 'Game is already finished'}, status=status.HTTP_400_BAD_REQUEST)
        
        game.status = 'abandoned'
        # Set winner as the other player if game was in progress
        if game.status == 'playing':
            if request.user == game.player1:
                game.winner = game.player2
            else:
                game.winner = game.player1
        
        game.save()
        
        serializer = self.get_serializer(game)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_games(self, request):
        """Get current user's games"""
        games = self.get_queryset()
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def waiting_games(self, request):
        """Get games waiting for players"""
        waiting_games = CaroGame.objects.filter(
            status='waiting'
        ).exclude(player1=request.user)
        
        serializer = self.get_serializer(waiting_games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active_games(self, request):
        """Get user's active games"""
        active_games = self.get_queryset().filter(status='playing')
        serializer = self.get_serializer(active_games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='rooms')
    def rooms(self, request):
        """Get list of waiting and playing rooms"""
        # Get waiting rooms (exclude user's own games)
        waiting_games = CaroGame.objects.filter(
            status='waiting'
        ).exclude(player1=request.user).order_by('-created_at')
        
        # Get playing rooms
        playing_games = CaroGame.objects.filter(
            status='playing'
        ).order_by('-updated_at')
        
        # Simplified serialization for list view
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
        
        return Response({
            'waiting': waiting_data,
            'playing': playing_data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's game statistics"""
        user = request.user
        games = self.get_queryset()
        
        total_games = games.filter(status='finished').count()
        games_won = games.filter(winner=user, status='finished').count()
        games_lost = games.filter(status='finished').exclude(
            Q(winner=user) | Q(winner__isnull=True)
        ).count()
        games_drawn = games.filter(winner__isnull=True, status='finished').count()
        
        win_rate = (games_won / total_games * 100) if total_games > 0 else 0
        
        # Calculate streaks (simplified)
        recent_games = games.filter(status='finished').order_by('-finished_at')[:10]
        current_streak = 0
        for game in recent_games:
            if game.winner == user:
                current_streak += 1
            else:
                break
        
        # For best streak, we'd need more complex logic or a separate field
        best_streak = current_streak  # Simplified
        
        stats_data = {
            'total_games': total_games,
            'games_won': games_won,
            'games_lost': games_lost,
            'games_drawn': games_drawn,
            'win_rate': win_rate,
            'current_streak': current_streak,
            'best_streak': best_streak,
        }
        
        serializer = CaroGameStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='create-room')
    def create_room(self, request):
        """Create a new game room"""
        serializer = CaroGameCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            game = serializer.save()
            game_serializer = CaroGameSerializer(game)
            return Response({
                'success': True,
                'message': 'Room created successfully',
                'game': game_serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='join-room')
    def join_room(self, request):
        """Join a game room by room_name"""
        room_name = request.data.get('room_name')
        
        if not room_name:
            return Response({
                'success': False,
                'message': 'room_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            game = CaroGame.objects.get(room_name=room_name, status='waiting')
        except CaroGame.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Room not found or already started'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if game.player1 == request.user:
            return Response({
                'success': False,
                'message': 'Cannot join your own game'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check user balance
        from user_wallet.models import Wallet
        try:
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance < 10000:
                return Response({
                    'success': False,
                    'message': 'Insufficient balance'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Deduct bet amount using model's method
            wallet.deduct_balance(
                amount=10000,
                transaction_type='game_bet',
                description=f'Bet for joining Caro game room: {room_name}'
            )
        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Join game
        game.player2 = request.user
        game.status = 'playing'
        game.total_pot = 20000
        game.winner_prize = 18000  # 90%
        game.house_fee = 2000  # 10%
        game.save()
        
        game_serializer = CaroGameSerializer(game)
        return Response({
            'success': True,
            'message': 'Joined room successfully',
            'game': game_serializer.data
        })

    @action(detail=False, methods=['post'], url_path='abandon-room')
    def abandon_room(self, request):
        """Abandon a game room by room_name"""
        room_name = request.data.get('room_name')
        
        if not room_name:
            return Response({
                'success': False,
                'message': 'room_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            game = CaroGame.objects.get(room_name=room_name)
        except CaroGame.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Room not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if request.user not in [game.player1, game.player2]:
            return Response({
                'success': False,
                'message': 'Not a player in this game'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if game.status == 'finished':
            return Response({
                'success': False,
                'message': 'Game is already finished'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine winner (opponent of person who abandoned)
        from user_wallet.models import Wallet
        
        if game.status == 'waiting':
            # If waiting, just cancel and refund
            wallet = Wallet.objects.get(user=game.player1)
            wallet.add_balance(
                amount=10000,
                transaction_type='game_refund',
                description=f'Refund for abandoned Caro game room: {room_name}',
                game=game
            )
            game.status = 'abandoned'
        else:
            # If playing, opponent wins
            if request.user == game.player1:
                game.winner = game.player2
            else:
                game.winner = game.player1
            
            # Award prize to winner
            winner_wallet = Wallet.objects.get(user=game.winner)
            winner_wallet.add_balance(
                amount=game.winner_prize,
                transaction_type='game_win',
                description=f'Won Caro game (opponent abandoned): {room_name}',
                game=game
            )
            
            game.status = 'abandoned'
        
        game.save()
        
        game_serializer = CaroGameSerializer(game)
        return Response({
            'success': True,
            'message': 'Game abandoned',
            'game': game_serializer.data
        })

    @action(detail=False, methods=['get'], url_path='room/(?P<room_name>[^/.]+)')
    def get_room(self, request, room_name=None):
        """Get game details by room_name"""
        try:
            game = CaroGame.objects.get(room_name=room_name)
            serializer = CaroGameSerializer(game)
            return Response({
                'success': True,
                'game': serializer.data
            })
        except CaroGame.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Room not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='user-stats')
    def user_stats(self, request):
        """Get user's caro game statistics"""
        user = request.user
        
        total_games_played = CaroGame.objects.filter(
            Q(player1=user) | Q(player2=user),
            status='finished'
        ).count()
        
        total_games_won = CaroGame.objects.filter(
            winner=user,
            status='finished'
        ).count()
        
        win_rate = (total_games_won / total_games_played * 100) if total_games_played > 0 else 0
        
        return Response({
            'success': True,
            'stats': {
                'total_games_played': total_games_played,
                'total_games_won': total_games_won,
                'win_rate': round(win_rate, 1)
            }
        })
