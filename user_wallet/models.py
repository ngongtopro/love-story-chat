from django.db import models
from django.contrib.auth.models import User


# ===========================
# WALLET MODELS
# ===========================
class Wallet(models.Model):
    """User wallet for managing in-game currency"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=100000)  # Start with 100,000 đồng
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['balance']),
        ]
    
    def __str__(self):
        return f'{self.user.username}: {self.balance:,} đồng'
    
    def has_sufficient_balance(self, amount):
        """Check if user has enough money"""
        return self.balance >= amount
    
    def deduct_balance(self, amount, transaction_type='game_bet', description='', game=None):
        """Deduct money from wallet"""
        if not self.has_sufficient_balance(amount):
            raise ValueError(f"Insufficient balance. Required: {amount:,}, Available: {self.balance:,}")
        
        self.balance -= amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=-amount,
            balance_after=self.balance,
            description=description,
            game=game
        )
        
        return True
    
    def add_balance(self, amount, transaction_type='game_win', description='', game=None):
        """Add money to wallet"""
        self.balance += amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.balance,
            description=description,
            game=game
        )
        
        return True


class WalletTransaction(models.Model):
    """Transaction history for wallet operations"""
    
    TRANSACTION_TYPES = [
        ('initial', 'Initial Balance'),
        ('game_bet', 'Game Bet'),
        ('game_win', 'Game Win'),
        ('game_loss', 'Game Loss'),
        ('game_refund', 'Game Refund'),
        ('admin_add', 'Admin Added'),
        ('admin_deduct', 'Admin Deducted'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()  # Positive for credit, negative for debit
    balance_after = models.IntegerField()  # Balance after this transaction
    description = models.TextField(blank=True)
    # Using string reference to avoid circular import - game field will reference CaroGame for both private and room games
    game = models.ForeignKey('caro_game.CaroGame', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
            models.Index(fields=['game']),
        ]
    
    def __str__(self):
        return f'{self.wallet.user.username}: {self.amount:+,} đồng ({self.get_transaction_type_display()})'
