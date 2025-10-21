from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CaroGame


class CaroGameSerializer(serializers.ModelSerializer):
    """Caro game serializer"""
    player1_username = serializers.CharField(source='player1.username', read_only=True)
    player2_username = serializers.CharField(source='player2.username', read_only=True)
    winner_username = serializers.CharField(source='winner.username', read_only=True)
    board = serializers.SerializerMethodField()
    
    class Meta:
        model = CaroGame
        fields = [
            'id', 'game_id', 'chat_id', 'player1', 'player2',
            'player1_username', 'player2_username', 
            'board_state', 'board', 'current_turn', 'status',
            'winner', 'winner_username', 'move_count', 'last_move',
            'created_at', 'updated_at', 'finished_at'
        ]
        read_only_fields = [
            'id', 'game_id', 'move_count', 'created_at', 
            'updated_at', 'finished_at'
        ]
    
    def get_board(self, obj):
        """Parse board state JSON"""
        try:
            return obj.get_board()
        except:
            return []


class CaroGameCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Caro games"""
    opponent_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = CaroGame
        fields = ['chat_id', 'opponent_id']
    
    def create(self, validated_data):
        player1 = self.context['request'].user
        opponent_id = validated_data.pop('opponent_id', None)
        
        player2 = None
        if opponent_id:
            try:
                player2 = User.objects.get(id=opponent_id)
            except User.DoesNotExist:
                raise serializers.ValidationError("Opponent not found")
        
        game = CaroGame.objects.create(
            player1=player1,
            player2=player2,
            **validated_data
        )
        
        return game


class CaroMoveSerializer(serializers.Serializer):
    """Serializer for making moves in Caro game"""
    row = serializers.IntegerField(min_value=0, max_value=14)
    col = serializers.IntegerField(min_value=0, max_value=14)
    
    def validate(self, data):
        game = self.context.get('game')
        if not game:
            raise serializers.ValidationError("Game not found")
        
        if game.status != 'playing':
            raise serializers.ValidationError("Game is not in progress")
        
        # Check if it's the player's turn
        user = self.context['request'].user
        if not game.is_player_turn(user):
            raise serializers.ValidationError("It's not your turn")
        
        # Check if position is valid
        if not game.is_valid_move(data['row'], data['col']):
            raise serializers.ValidationError("Invalid move position")
        
        return data


class CaroGameStatsSerializer(serializers.Serializer):
    """Serializer for Caro game statistics"""
    total_games = serializers.IntegerField()
    games_won = serializers.IntegerField()
    games_lost = serializers.IntegerField()
    games_drawn = serializers.IntegerField()
    win_rate = serializers.FloatField()
    current_streak = serializers.IntegerField()
    best_streak = serializers.IntegerField()
