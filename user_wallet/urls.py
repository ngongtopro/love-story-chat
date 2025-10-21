from django.urls import path
from . import views

app_name = 'user_wallet'

urlpatterns = [
    # Wallet main page
    path('', views.wallet_view, name='wallet'),
    
    # Wallet API endpoints
    path('api/balance/', views.wallet_balance_api, name='wallet_balance_api'),
]
