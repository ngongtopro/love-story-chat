from django.db import models
from django.contrib.auth.models import User
import json


# ===========================
# CARO GAME MODELS
# ===========================
class CaroGame(models.Model):
    """Caro (Tic-tac-toe) game between two users in private chat"""
    
    GAME_STATUS_CHOICES = [
        ('waiting', 'Waiting for Player'),
        ('playing', 'In Progress'),
        ('finished', 'Finished'),
        ('abandoned', 'Abandoned'),
    ]
    
    # Game identification
    chat_id = models.CharField(max_length=100, db_index=True)  # Reference to chat without direct FK
    game_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Players
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caro_games_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caro_games_as_player2', null=True, blank=True)
    
    # Game state
    board_state = models.TextField(default='[]')  # JSON string of 15x15 board
    current_turn = models.CharField(max_length=20, default='X')  # 'X' or 'O'
    status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='waiting', db_index=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_caro_games', null=True, blank=True)
    
    # Game settings
    board_size = models.IntegerField(default=15)
    win_condition = models.IntegerField(default=5)  # Number in a row to win
    
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
            models.Index(fields=['chat_id', 'status']),
            models.Index(fields=['game_id']),
            models.Index(fields=['player1', '-created_at']),
            models.Index(fields=['player2', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f'Caro Game {self.game_id}: {self.player1.username} vs {self.player2.username if self.player2 else "waiting"}'
    
    def save(self, *args, **kwargs):
        if not self.game_id:
            self.game_id = f"caro_{self.chat_id}_{self.created_at.strftime('%Y%m%d_%H%M%S')}"
        super().save(*args, **kwargs)
    
    def get_board(self):
        """Get board as 2D array"""
        try:
            board = json.loads(self.board_state) if self.board_state else None
            if board is None or len(board) != self.board_size:
                return self._create_empty_board()
            return board
        except (json.JSONDecodeError, TypeError):
            return self._create_empty_board()
    
    def set_board(self, board):
        """Set board from 2D array"""
        self.board_state = json.dumps(board)
    
    def _create_empty_board(self):
        """Create empty board"""
        return [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
    
    def make_move(self, row, col, player_symbol):
        """Make a move on the board"""
        board = self.get_board()
        if 0 <= row < self.board_size and 0 <= col < self.board_size and board[row][col] == '':
            board[row][col] = player_symbol
            self.set_board(board)
            self.total_moves += 1
            return True
        return False
    
    def check_winner(self):
        """Check if there's a winner"""
        board = self.get_board()
        
        # Check all possible winning combinations
        directions = [(0,1), (1,0), (1,1), (1,-1)]  # horizontal, vertical, diagonal
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if board[row][col]:
                    symbol = board[row][col]
                    for dr, dc in directions:
                        count = 1
                        # Check forward direction
                        r, c = row + dr, col + dc
                        while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r][c] == symbol:
                            count += 1
                            r, c = r + dr, c + dc
                        
                        # Check backward direction
                        r, c = row - dr, col - dc
                        while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r][c] == symbol:
                            count += 1
                            r, c = r - dr, c - dc
                        
                        if count >= self.win_condition:
                            return symbol
        return None
    
    def is_board_full(self):
        """Check if board is full (draw condition)"""
        board = self.get_board()
        for row in board:
            for cell in row:
                if cell == '':
                    return False
        return True

    @classmethod
    def get_active_game(cls, chat_id):
        """Get active game for chat"""
        return cls.objects.filter(
            chat_id=chat_id,
            status__in=['waiting', 'playing']
        ).first()

    @classmethod
    def create_game(cls, player1, chat_id):
        """Create new Caro game for chat"""
        game = cls.objects.create(
            chat_id=chat_id,
            player1=player1
        )
        return game

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
        
        # Make the move
        if self.make_move(row, col, current_symbol):
            from django.utils import timezone
            
            # Check for winner
            winner_symbol = self.check_winner()
            if winner_symbol:
                self.status = 'finished'
                self.winner = self.player1 if winner_symbol == 'X' else self.player2
                self.finished_at = timezone.now()
                if self.started_at:
                    self.game_duration = self.finished_at - self.started_at
                
                # Update player statistics
                winner_profile = getattr(self.winner, 'profile', None)
                loser_profile = getattr(self.player1 if self.winner == self.player2 else self.player2, 'profile', None)
                
                if winner_profile:
                    winner_profile.update_game_stats(won=True)
                if loser_profile:
                    loser_profile.update_game_stats(won=False)
                    
            elif self.is_board_full():
                # Draw
                self.status = 'finished'
                self.finished_at = timezone.now()
                if self.started_at:
                    self.game_duration = self.finished_at - self.started_at
                
                # Update both players statistics (no winner)
                p1_profile = getattr(self.player1, 'profile', None)
                p2_profile = getattr(self.player2, 'profile', None)
                if p1_profile:
                    p1_profile.update_game_stats(won=False)
                if p2_profile:
                    p2_profile.update_game_stats(won=False)
            else:
                # Continue game
                self.current_turn = 'O' if current_symbol == 'X' else 'X'
            
            self.save()
            return True, "Move successful"
        
        return False, "Invalid move"
    
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
        return {
            'id': self.id,
            'game_id': self.game_id,
            'chat_id': self.chat_id,
            'player1': {
                'username': self.player1.username,
                'display_name': getattr(self.player1.profile, 'name', self.player1.username) if hasattr(self.player1, 'profile') else self.player1.username
            },
            'player2': {
                'username': self.player2.username,
                'display_name': getattr(self.player2.profile, 'name', self.player2.username) if hasattr(self.player2, 'profile') else self.player2.username
            } if self.player2 else None,
            'board_state': self.get_board(),
            'current_turn': self.current_turn,
            'status': self.status,
            'winner': {
                'username': self.winner.username,
                'display_name': getattr(self.winner.profile, 'name', self.winner.username) if hasattr(self.winner, 'profile') else self.winner.username
            } if self.winner else None,
            'board_size': self.board_size,
            'win_condition': self.win_condition,
            'total_moves': self.total_moves,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
        }


class RoomCaroGame(models.Model):
    """Caro game for chat rooms (room-based, not private chat) with betting system"""
    
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
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_caro_games_as_player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_caro_games_as_player2', null=True, blank=True)
    
    # Game state
    board_state = models.TextField(default='[]')  # JSON string of 15x15 board
    current_turn = models.CharField(max_length=20, default='X')  # 'X' or 'O'
    status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default='waiting', db_index=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='won_room_caro_games', null=True, blank=True)
    
    # Betting system
    bet_amount = models.IntegerField(default=10000)  # Amount each player bets
    total_pot = models.IntegerField(default=0)  # Total money in the pot
    winner_prize = models.IntegerField(default=0)  # Amount winner receives (90%)
    house_fee = models.IntegerField(default=0)  # House fee (10%)
    
    # Game settings
    board_size = models.IntegerField(default=15)
    win_condition = models.IntegerField(default=5)  # Number in a row to win
    
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
        return f'Room Caro Game {self.game_id}: {self.player1.username} vs {self.player2.username if self.player2 else "waiting"}'
    
    def save(self, *args, **kwargs):
        if not self.game_id:
            from django.utils import timezone
            self.game_id = f"room_caro_{self.room_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate betting amounts
        if self.bet_amount and not self.total_pot:
            self.total_pot = self.bet_amount * 2  # Both players bet
            self.winner_prize = int(self.total_pot * 0.9)  # 90% to winner
            self.house_fee = self.total_pot - self.winner_prize  # 10% house fee
            
        super().save(*args, **kwargs)
    
    def get_board(self):
        """Get board as 2D array"""
        try:
            board = json.loads(self.board_state) if self.board_state else None
            if board is None or len(board) != self.board_size:
                return self._create_empty_board()
            return board
        except (json.JSONDecodeError, TypeError):
            return self._create_empty_board()
    
    def set_board(self, board):
        """Set board from 2D array"""
        self.board_state = json.dumps(board)
    
    def _create_empty_board(self):
        """Create empty board"""
        return [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
    
    def make_move(self, row, col, player_symbol):
        """Make a move on the board with auto-expansion"""
        board = self.get_board()
        current_size = len(board)
        
        # Check for valid coordinates
        if row < 0 or row >= current_size or col < 0 or col >= current_size:
            return False
            
        # Check if cell is already occupied
        if board[row][col] != '':
            return False
        
        # Check if move is on the edge - if so, expand board
        if row == 0 or row == current_size - 1 or col == 0 or col == current_size - 1:
            board = self._expand_board(board)
            # Adjust coordinates for expanded board (add 1 because we add border around)
            row += 1
            col += 1
        
        # Make the move
        board[row][col] = player_symbol
        self.set_board(board)
        self.board_size = len(board)  # Update board size
        self.total_moves += 1
        return True
    
    def _expand_board(self, board):
        """Expand board by adding one row/column on each side"""
        current_size = len(board)
        new_size = current_size + 2  # Add 1 row/col on each side
        
        # Create new expanded board
        new_board = [['' for _ in range(new_size)] for _ in range(new_size)]
        
        # Copy old board to center of new board
        for i in range(current_size):
            for j in range(current_size):
                new_board[i + 1][j + 1] = board[i][j]
        
        return new_board
    
    def check_winner(self):
        """Check if there's a winner on the board"""
        board = self.get_board()
        board_size = len(board)  # Use actual board size, not self.board_size
        
        for row in range(board_size):
            for col in range(board_size):
                symbol = board[row][col]
                if symbol == '':
                    continue
                    
                # Check all 4 directions: horizontal, vertical, diagonal1, diagonal2
                directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                
                for dr, dc in directions:
                    count = 1
                    
                    # Check forward direction
                    r, c = row + dr, col + dc
                    while 0 <= r < board_size and 0 <= c < board_size and board[r][c] == symbol:
                        count += 1
                        r, c = r + dr, c + dc
                    
                    # Check backward direction
                    r, c = row - dr, col - dc
                    while 0 <= r < board_size and 0 <= c < board_size and board[r][c] == symbol:
                        count += 1
                        r, c = r - dr, c - dc
                    
                    if count >= self.win_condition:
                        return symbol
        return None


# ===========================
# UTILITY FUNCTIONS FOR ROOM-BASED CARO GAMES
# ===========================
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def get_active_game(room_name: str):
    """Get active Caro game for room with betting info"""
    try:
        game = RoomCaroGame.objects.filter(
            room_name=room_name,
            status__in=['waiting', 'playing']
        ).first()
        
        if game:
            return {
                'id': game.id,
                'room_name': game.room_name,
                'player1': game.player1.username,
                'player2': game.player2.username if game.player2 else None,
                'board_state': game.get_board(),
                'current_turn': game.current_turn,
                'status': game.status,
                'winner': game.winner.username if game.winner else None,
                'created_at': game.created_at,
                'updated_at': game.updated_at,
                'bet_amount': game.bet_amount,
                'total_pot': game.total_pot,
                'winner_prize': game.winner_prize,
                'house_fee': game.house_fee
            }
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
                        old_game = RoomCaroGame.objects.get(id=existing_game.get('id'))
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
        game = RoomCaroGame.objects.create(
            room_name=room_name,
            player1=player1
        )
        
        logger.info(f"Game created by {player1_username} in room {room_name}, bet amount deducted: 10,000")
        
        return {
            'id': game.id,
            'room_name': game.room_name,
            'player1': game.player1.username,
            'player2': None,
            'board_state': game.get_board(),
            'current_turn': game.current_turn,
            'status': game.status,
            'winner': None,
            'created_at': game.created_at,
            'updated_at': game.updated_at,
            'bet_amount': game.bet_amount,
            'total_pot': game.total_pot
        }
    except User.DoesNotExist:
        logger.error(f"User {player1_username} not found")
        return {'error': 'user_not_found'}
    except Exception as e:
        logger.error(f"Error creating Caro game: {e}")
        return {'error': 'creation_failed'}

def make_move(game_id: str, row: int, col: int, player_username: str):
    """Make a move in Caro game"""
    try:
        from django.contrib.auth.models import User
        game = RoomCaroGame.objects.get(id=int(game_id))
        
        if game.status != 'playing':
            return None
        
        player = User.objects.get(username=player_username)
        
        # Check if it's player's turn
        current_symbol = 'X' if game.player1 == player else 'O'
        if (current_symbol == 'X' and game.current_turn != 'X') or \
           (current_symbol == 'O' and game.current_turn != 'O'):
            return None
        
        # Make the move
        if game.make_move(row, col, current_symbol):
            # Check for winner
            winner_symbol = game.check_winner()
            if winner_symbol:
                game.status = 'finished'
                game.winner = game.player1 if winner_symbol == 'X' else game.player2
                
                # Distribute prize money to winner
                winner_wallet = game.winner.wallet
                prize_amount = game.winner_prize
                
                if winner_wallet.add_balance(
                    prize_amount, 
                    'caro_win', 
                    f'Won Caro game in room {game.room_name}', 
                    game
                ):
                    logger.info(f"Prize {prize_amount} awarded to winner {game.winner.username}")
                else:
                    logger.error(f"Failed to award prize to winner {game.winner.username}")
                    
            else:
                game.current_turn = 'O' if current_symbol == 'X' else 'X'
            
            game.save()
            
            return {
                'id': game.id,
                'room_name': game.room_name,
                'player1': game.player1.username,
                'player2': game.player2.username if game.player2 else None,
                'board_state': game.get_board(),
                'current_turn': game.current_turn,
                'status': game.status,
                'winner': game.winner.username if game.winner else None,
                'created_at': game.created_at,
                'updated_at': game.updated_at,
                'bet_amount': game.bet_amount,
                'total_pot': game.total_pot,
                'winner_prize': game.winner_prize if game.winner else None
            }
    except Exception as e:
        logger.error(f"Error making move in Caro game: {e}")
    
    return None

def join_game(room_name: str, player2_username: str):
    """Join existing Caro game with wallet check"""
    try:
        from django.contrib.auth.models import User
        from user_wallet.models import Wallet
        
        # Find the waiting game
        game = RoomCaroGame.objects.filter(
            room_name=room_name,
            status='waiting'
        ).first()
        
        if not game:
            logger.warning(f"No waiting game found in room {room_name}")
            return {'error': 'no_game', 'success': False}
            
        player2 = User.objects.get(username=player2_username)
        
        # Check if player2 is trying to join their own game
        if game.player1 == player2:
            logger.warning(f"Player {player2_username} trying to join their own game")
            return {'error': 'own_game', 'success': False}
        
        # Check if player2 has wallet and sufficient balance
        try:
            wallet = player2.wallet
            if not wallet.has_sufficient_balance(10000):
                logger.warning(f"Player {player2_username} has insufficient balance: {wallet.balance}")
                return {'error': 'insufficient_balance', 'balance': wallet.balance, 'success': False}
        except Wallet.DoesNotExist:
            logger.error(f"Player {player2_username} doesn't have a wallet")
            return {'error': 'no_wallet', 'success': False}
        
        # Deduct bet amount from player2's wallet
        if not wallet.deduct_balance(10000, 'caro_bet', f'Bet for Caro game in room {room_name}', game):
            logger.error(f"Failed to deduct bet from player {player2_username}")
            return {'error': 'payment_failed', 'success': False}
        
        # Join the game
        game.player2 = player2
        game.status = 'playing'
        game.save()  # This will automatically update total_pot and winner_prize in save() method
        
        logger.info(f"Player {player2_username} joined game in room {room_name}, total pot now: {game.total_pot}")
        
        return {
            'success': True,
            'game': {
                'id': game.id,
                'room_name': game.room_name,
                'player1': game.player1.username,
                'player2': game.player2.username,
                'board_state': game.get_board(),
                'current_turn': game.current_turn,
                'status': game.status,
                'bet_amount': game.bet_amount,
                'total_pot': game.total_pot,
                'winner_prize': game.winner_prize
            }
        }
        
    except User.DoesNotExist:
        logger.error(f"User {player2_username} not found")
        return {'error': 'user_not_found', 'success': False}
    except Exception as e:
        logger.error(f"Error joining Caro game: {e}")
        return {'error': 'join_failed', 'success': False}

def abandon_game(room_name: str, player_username: str):
    """Abandon Caro game with refund logic"""
    try:
        from django.contrib.auth.models import User
        
        game = RoomCaroGame.objects.filter(
            room_name=room_name,
            status__in=['waiting', 'playing']
        ).first()
        
        if not game:
            return False
        
        player = User.objects.get(username=player_username)
        
        # Handle refunds based on game status
        if game.status == 'waiting':
            # If game is still waiting (only player1), refund the bet
            if game.player1 == player:
                player1_wallet = game.player1.wallet
                if player1_wallet.add_balance(
                    10000, 
                    'caro_refund', 
                    f'Refund for abandoned Caro game in room {room_name}', 
                    game
                ):
                    logger.info(f"Refunded 10,000 to {game.player1.username} for abandoned waiting game")
                
        elif game.status == 'playing':
            # If game is playing (both players), refund both
            player1_wallet = game.player1.wallet
            player2_wallet = game.player2.wallet
            
            if player1_wallet.add_balance(
                10000, 
                'caro_refund', 
                f'Refund for abandoned Caro game in room {room_name}', 
                game
            ):
                logger.info(f"Refunded 10,000 to {game.player1.username} for abandoned playing game")
                
            if player2_wallet.add_balance(
                10000, 
                'caro_refund', 
                f'Refund for abandoned Caro game in room {room_name}', 
                game
            ):
                logger.info(f"Refunded 10,000 to {game.player2.username} for abandoned playing game")
        
        game.status = 'abandoned'
        game.save()
        return True
        
    except Exception as e:
        logger.error(f"Error abandoning Caro game: {e}")
        return False



