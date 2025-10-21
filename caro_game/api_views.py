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
