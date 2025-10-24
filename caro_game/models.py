from django.db import models
from django.contrib.auth.models import User
import json


# ===========================
# CARO GAME MODELS
# ===========================
class CaroMove(models.Model):
    """Model to track each move in a Caro game"""
    game = models.ForeignKey('CaroGame', on_delete=models.CASCADE, related_name='moves')
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    row = models.IntegerField()
    col = models.IntegerField()
    symbol = models.CharField(max_length=1)  # 'X' or 'O'
    move_number = models.IntegerField()  # Sequential move number
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['move_number']
        indexes = [
            models.Index(fields=['game', 'move_number']),
        ]
    
    def __str__(self):
        return f"Move {self.move_number}: {self.symbol} at ({self.row}, {self.col})"


class CaroGame(models.Model):
    """Caro (Tic-tac-toe) room game with betting system"""
    
    GAME_STATUS_CHOICES = [
        ('waiting', 'Waiting for Player'),
        ('playing', 'In Progress'),
        ('finished', 'Finished'),
        ('abandoned', 'Abandoned'),
    ]
       
    # Game identification
    room_name = models.CharField(max_length=100, db_index=True)
    game_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Players
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caro_games_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caro_games_as_player2', null=True, blank=True)
    
    # Game state
    current_turn = models.CharField(max_length=20, default='X')  # 'X' or 'O'
    status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='waiting', db_index=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_caro_games', null=True, blank=True)
    win_condition = models.IntegerField(default=5)  # Number in a row to win
    
    # Betting system
    bet_amount = models.IntegerField(default=10000)  # Amount each player bets
    total_pot = models.IntegerField(default=0)  # Total money in the pot
    winner_prize = models.IntegerField(default=0)  # Amount winner receives (90%)
    house_fee = models.IntegerField(default=0)  # House fee (10%)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    # Game statistics
    total_moves = models.IntegerField(default=0)
    game_duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room_name', 'status']),
            models.Index(fields=['game_id']),
            models.Index(fields=['player1', '-created_at']),
            models.Index(fields=['player2', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f'Caro Game {self.game_id}: {self.player1.username} vs {self.player2.username if self.player2 else "waiting"}'
    
    def save(self, *args, **kwargs):
        if not self.game_id:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%H%M%S_%d%m%Y')
            self.game_id = f"caro_{self.room_name}_{timestamp}"
        
        # Calculate betting amounts
        if self.bet_amount and not self.total_pot:
            self.total_pot = self.bet_amount * 2  # Both players bet
            self.winner_prize = int(self.total_pot * 0.9)  # 90% to winner
            self.house_fee = self.total_pot - self.winner_prize  # 10% house fee
            
        super().save(*args, **kwargs)
    
    def get_moves_list(self):
        """Get queryset of all moves in order"""
        return self.moves.all().select_related('player')

    def join_game(self, player2):
        """Join existing game"""
        if self.status != 'waiting' or self.player2:
            return False
        
        from django.utils import timezone
        self.player2 = player2
        self.status = 'playing'
        self.started_at = timezone.now()
        self.save()
        return True

    def make_game_move(self, row, col, player):
        """Make a move in the game"""
        if self.status != 'playing':
            return False, "Game is not in playing status"
        
        # Check if it's player's turn
        current_symbol = 'X' if self.player1 == player else 'O'
        if (current_symbol == 'X' and self.current_turn != 'X') or \
           (current_symbol == 'O' and self.current_turn != 'O'):
            return False, "Not your turn"
        
        # Check if move already exists at this position
        if self.moves.filter(row=row, col=col).exists():
            return False, "Position already occupied"
        
        # Create the move
        CaroMove.objects.create(
            game=self,
            player=player,
            row=row,
            col=col,
            symbol=current_symbol,
            move_number=self.total_moves + 1
        )
        
        self.total_moves += 1
        
        from django.utils import timezone
        
        # Check for winner
        winner_symbol = self.check_winner()
        if winner_symbol:
            self.status = 'finished'
            self.winner = self.player1 if winner_symbol == 'X' else self.player2
            self.finished_at = timezone.now()
            if self.started_at:
                self.game_duration = self.finished_at - self.started_at
            
            # Award prize to winner
            if self.winner and self.winner_prize > 0:
                try:
                    winner_wallet = self.winner.wallet
                    winner_wallet.add_balance(
                        self.winner_prize,
                        'caro_win',
                        f'Won Caro game in room {self.room_name}',
                        self
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error awarding prize: {e}")
        else:
            # Continue game - switch turn
            self.current_turn = 'O' if current_symbol == 'X' else 'X'
        
        self.save()
        return True, "Move successful"
    
    def check_winner(self):
        """Check if there's a winner based on moves"""
        moves = self.get_moves_list()
        if not moves:
            return None
        
        # Build board from moves
        move_dict = {}
        for move in moves:
            move_dict[(move.row, move.col)] = move.symbol
        
        if not move_dict:
            return None
        
        # Find board boundaries
        rows = [r for r, c in move_dict.keys()]
        cols = [c for r, c in move_dict.keys()]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        
        # Check all positions for winning patterns
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # horizontal, vertical, diagonal
        
        for (row, col), symbol in move_dict.items():
            for dr, dc in directions:
                count = 1
                
                # Check forward direction
                r, c = row + dr, col + dc
                while (r, c) in move_dict and move_dict[(r, c)] == symbol:
                    count += 1
                    r, c = r + dr, c + dc
                
                # Check backward direction
                r, c = row - dr, col - dc
                while (r, c) in move_dict and move_dict[(r, c)] == symbol:
                    count += 1
                    r, c = r - dr, c - dc
                
                if count >= self.win_condition:
                    return symbol
        
        return None
    
    def abandon_game(self, player):
        """Abandon game by player"""
        if self.status not in ['waiting', 'playing']:
            return False
        
        from django.utils import timezone
        self.status = 'abandoned'
        self.finished_at = timezone.now()
        
        # If game was in progress, other player wins
        if self.status == 'playing' and self.player2:
            self.winner = self.player2 if player == self.player1 else self.player1
            
            # Update statistics
            winner_profile = getattr(self.winner, 'profile', None)
            loser_profile = getattr(player, 'profile', None)
            
            if winner_profile:
                winner_profile.update_game_stats(won=True)
            if loser_profile:
                loser_profile.update_game_stats(won=False)
        
        self.save()
        return True

    def to_dict(self):
        """Convert to dictionary for API responses"""
        # Serialize moves
        moves_data = [
            {
                'row': move.row,
                'col': move.col,
                'symbol': move.symbol,
                'move_number': move.move_number,
                'player_username': move.player.username,
                'timestamp': move.timestamp.isoformat()
            }
            for move in self.get_moves_list()
        ]
        
        return {
            'id': self.id,
            'game_id': self.game_id,
            'room_name': self.room_name,
            'player1': {
                'username': self.player1.username,
                'display_name': getattr(self.player1.profile, 'name', self.player1.username) if hasattr(self.player1, 'profile') else self.player1.username
            },
            'player2': {
                'username': self.player2.username,
                'display_name': getattr(self.player2.profile, 'name', self.player2.username) if hasattr(self.player2, 'profile') else self.player2.username
            } if self.player2 else None,
            'moves': moves_data,
            'current_turn': self.current_turn,
            'status': self.status,
            'winner': {
                'username': self.winner.username,
                'display_name': getattr(self.winner.profile, 'name', self.winner.username) if hasattr(self.winner, 'profile') else self.winner.username
            } if self.winner else None,
            'win_condition': self.win_condition,
            'total_moves': self.total_moves,
            'bet_amount': self.bet_amount,
            'total_pot': self.total_pot,
            'winner_prize': self.winner_prize,
            'house_fee': self.house_fee,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
        }


# ===========================
# UTILITY FUNCTIONS FOR CARO GAMES
# ===========================
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_active_game(room_name: str):
    """Get active Caro game for room with betting info"""
    try:
        game = CaroGame.objects.filter(
            room_name=room_name,
            status__in=['waiting', 'playing']
        ).first()
        
        if game:
            return game.to_dict()
    except Exception as e:
        logger.error(f"Error getting Caro game from database: {e}")
    
    return None

def create_game(room_name: str, player1_username: str):
    """Create new Caro game with wallet check and active game validation"""
    try:
        from django.contrib.auth.models import User
        from user_wallet.models import Wallet
        from datetime import datetime, timezone, timedelta
        
        player1 = User.objects.get(username=player1_username)
        
        # Check if there's already an active game in this room
        existing_game = get_active_game(room_name)
        if existing_game:
            if existing_game.get('status') == 'playing':
                return {'error': 'game_in_progress', 'message': f'Room "{room_name}" has a game in progress. Please choose a different name.'}
            elif existing_game.get('status') == 'waiting':
                # Check if the waiting game is old (more than 10 minutes)
                game_age = datetime.now(timezone.utc) - existing_game.get('created_at')
                
                if game_age > timedelta(minutes=10):
                    # Remove old waiting game
                    try:
                        old_game = CaroGame.objects.get(id=existing_game.get('id'))
                        # Refund the player
                        try:
                            old_wallet = old_game.player1.wallet
                            old_wallet.add_balance(10000, 'caro_refund', f'Refund for expired game in room {room_name}')
                            logger.info(f"Refunded 10,000 to {old_game.player1.username} for expired game")
                        except Exception as refund_error:
                            logger.error(f"Error refunding player: {refund_error}")
                        
                        old_game.delete()
                        logger.info(f"Removed old waiting game in room {room_name}")
                    except Exception as delete_error:
                        logger.error(f"Error deleting old game: {delete_error}")
                        return {'error': 'cleanup_failed', 'message': 'Failed to clean up old game'}
                else:
                    # Game is waiting and recent
                    if existing_game.get('player1') == player1_username:
                        # User is trying to create again, return existing game
                        return existing_game
                    else:
                        # Suggest joining the existing game
                        return {
                            'error': 'game_waiting', 
                            'message': f'Room "{room_name}" has a game waiting for players. Please join the existing game or choose a different name.',
                            'existing_game': existing_game
                        }
        
        # Check if player1 has wallet and sufficient balance
        try:
            wallet = player1.wallet
            if not wallet.has_sufficient_balance(10000):
                logger.warning(f"Player {player1_username} has insufficient balance: {wallet.balance}")
                return {'error': 'insufficient_balance', 'balance': wallet.balance}
        except Wallet.DoesNotExist:
            logger.error(f"Player {player1_username} doesn't have a wallet")
            return {'error': 'no_wallet'}
        
        # Deduct bet amount from player1's wallet
        if not wallet.deduct_balance(10000, 'caro_bet', f'Bet for Caro game in room {room_name}'):
            logger.error(f"Failed to deduct bet from player {player1_username}")
            return {'error': 'payment_failed'}
        
        # Create the game
        game = CaroGame.objects.create(
            room_name=room_name,
            player1=player1,
            bet_amount=10000
        )
        
        logger.info(f"Game created by {player1_username} in room {room_name}, bet amount deducted: 10,000")
        
        return game.to_dict()
    except User.DoesNotExist:
        logger.error(f"User {player1_username} not found")
        return {'error': 'user_not_found'}
    except Exception as e:
        logger.error(f"Error creating Caro game: {e}")
        return {'error': 'creation_failed'}
