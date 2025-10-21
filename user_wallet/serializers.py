from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Wallet, WalletTransaction


class WalletSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'balance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    wallet = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'wallet', 'transaction_type', 'amount',
            'balance_after', 'description', 'game', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AddBalanceSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    description = serializers.CharField(max_length=255, required=False, default='Admin Added')
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class DeductBalanceSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    description = serializers.CharField(max_length=255, required=False, default='Admin Deducted')
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        amount = attrs['amount']
        
        try:
            wallet = user.wallet
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("User does not have a wallet")
        
        if not wallet.has_sufficient_balance(amount):
            raise serializers.ValidationError("Insufficient balance")
        
        attrs['wallet'] = wallet
        return attrs


class WalletStatsSerializer(serializers.Serializer):
    total_transactions = serializers.IntegerField()
    total_earned = serializers.IntegerField()
    total_spent = serializers.IntegerField()
    current_balance = serializers.IntegerField()
    recent_transactions = WalletTransactionSerializer(many=True)
