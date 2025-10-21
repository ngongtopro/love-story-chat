from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Sum, Count

from .models import Wallet, WalletTransaction
from .serializers import (
    WalletSerializer, WalletTransactionSerializer,
    AddBalanceSerializer, DeductBalanceSerializer,
    WalletStatsSerializer
)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user wallets
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create user's wallet"""
        wallet, created = Wallet.objects.get_or_create(
            user=self.request.user,
            defaults={'balance': 100000}  # Default starting balance
        )
        return wallet

    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        """Get current user's wallet"""
        wallet = self.get_object()
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_balance(self, request):
        """Add balance to wallet (admin function or game rewards)"""
        serializer = AddBalanceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        description = serializer.validated_data['description']
        
        wallet = self.get_object()
        wallet.add_balance(amount, 'admin_add', description)
        
        return Response({
            'message': f'Added {amount:,} đồng to wallet',
            'wallet': self.get_serializer(wallet).data
        })

    @action(detail=False, methods=['post'])
    def deduct_balance(self, request):
        """Deduct balance from wallet"""
        serializer = DeductBalanceSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        description = serializer.validated_data['description']
        wallet = serializer.validated_data['wallet']
        
        try:
            wallet.deduct_balance(amount, 'admin_deduct', description)
            
            return Response({
                'message': f'Deducted {amount:,} đồng from wallet',
                'wallet': self.get_serializer(wallet).data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get wallet statistics"""
        wallet = self.get_object()
        transactions = wallet.transactions.all()
        
        # Calculate stats
        total_transactions = transactions.count()
        
        earned_transactions = transactions.filter(amount__gt=0)
        spent_transactions = transactions.filter(amount__lt=0)
        
        total_earned = earned_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        total_spent = abs(spent_transactions.aggregate(Sum('amount'))['amount__sum'] or 0)
        
        recent_transactions = transactions[:10]
        
        stats_data = {
            'total_transactions': total_transactions,
            'total_earned': total_earned,
            'total_spent': total_spent,
            'current_balance': wallet.balance,
            'recent_transactions': recent_transactions
        }
        
        serializer = WalletStatsSerializer(stats_data)
        return Response(serializer.data)


class WalletTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for wallet transactions
    """
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['transaction_type']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        try:
            wallet = user.wallet
            return WalletTransaction.objects.filter(wallet=wallet)
        except Wallet.DoesNotExist:
            return WalletTransaction.objects.none()

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent transactions"""
        transactions = self.get_queryset()[:20]
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def earnings(self, request):
        """Get earning transactions only"""
        transactions = self.get_queryset().filter(amount__gt=0)
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expenses(self, request):
        """Get expense transactions only"""
        transactions = self.get_queryset().filter(amount__lt=0)
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
