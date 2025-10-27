from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CaroGame


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add display_name
        display_name = data.get('first_name') or data.get('username')
        data['display_name'] = display_name
        return data


class CaroMoveDetailSerializer(serializers.Serializer):
    """Serializer for move details"""
    row = serializers.IntegerField()
    col = serializers.IntegerField()
    symbol = serializers.CharField()
    move_number = serializers.IntegerField()
    player_username = serializers.CharField()
    timestamp = serializers.DateTimeField()


class CaroGameSerializer(serializers.ModelSerializer):
    """Caro game serializer"""
    player1 = UserSimpleSerializer(read_only=True)
    player2 = UserSimpleSerializer(read_only=True, allow_null=True)
    winner = UserSimpleSerializer(read_only=True, allow_null=True)
    moves = serializers.SerializerMethodField()
    
    class Meta:
        model = CaroGame
        fields = [
            'id', 'game_id', 'room_name', 
            'player1', 'player2', 'winner',
            'current_turn', 'status', 'win_condition',
            'total_moves', 'moves',
            'bet_amount', 'total_pot', 'winner_prize', 'house_fee',
            'created_at', 'updated_at', 'started_at', 'finished_at'
        ]
        read_only_fields = [
            'id', 'game_id', 'total_moves', 
            'created_at', 'updated_at', 'started_at', 'finished_at'
        ]
    
    def get_moves(self, obj):
        """Get all moves for the game"""
        moves = obj.moves.all().order_by('move_number')
        return [{
            'row': move.row,
            'col': move.col,
            'symbol': move.symbol,
            'move_number': move.move_number,
            'player_username': move.player.username,
            'timestamp': move.timestamp.isoformat(),
        } for move in moves]


class CaroGameCreateSerializer(serializers.Serializer):
    """Serializer for creating Caro games"""
    room_name = serializers.CharField(min_length=3, max_length=30)
    
    def validate_room_name(self, value):
        """Check if room name already exists"""
        if CaroGame.objects.filter(room_name=value, status__in=['waiting', 'playing']).exists():
            raise serializers.ValidationError("Room name already exists")
        return value
    
    def create(self, validated_data):
        player1 = self.context['request'].user
        room_name = validated_data['room_name']
        
        # Check user balance (assuming 10,000 coins bet)
        from user_wallet.models import Wallet
        try:
            wallet = Wallet.objects.get(user=player1)
            if wallet.balance < 10000:
                raise serializers.ValidationError("Insufficient balance")
            
            # Deduct bet amount using the model's method
            wallet.deduct_balance(
                amount=10000,
                transaction_type='game_bet',
                description=f'Bet for Caro game room: {room_name}'
            )
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found")
        
        game = CaroGame.objects.create(
            player1=player1,
            room_name=room_name,
            bet_amount=10000,
            total_pot=10000,
            status='waiting'
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
