from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import WalletViewSet, WalletTransactionViewSet

router = DefaultRouter()
router.register('wallets', WalletViewSet, basename='wallets')
router.register('transactions', WalletTransactionViewSet, basename='wallet-transactions')

urlpatterns = [
    path('api/wallet/', include(router.urls)),
]
