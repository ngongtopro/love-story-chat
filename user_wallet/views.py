from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Wallet, WalletTransaction
import logging

logger = logging.getLogger(__name__)


@login_required
def wallet_view(request):
    """Display user's wallet information"""
    try:
        wallet = request.user.wallet
        
        # Get recent transactions (last 20)
        recent_transactions = wallet.transactions.all()[:20]
        
        return render(request, 'user_wallet/wallet.html', {
            'wallet': wallet,
            'recent_transactions': recent_transactions,
        })
        
    except Exception as e:
        logger.error(f"Error loading wallet for user {request.user.username}: {e}")
        return render(request, 'user_wallet/wallet.html', {
            'error': 'Unable to load wallet information'
        })


@login_required 
@csrf_exempt
def wallet_balance_api(request):
    """API endpoint to get current wallet balance"""
    if request.method == 'GET':
        try:
            wallet = request.user.wallet
            return JsonResponse({
                'success': True,
                'balance': wallet.balance,
                'formatted_balance': f"{wallet.balance:,} đồng"
            })
        except Exception as e:
            logger.error(f"Error getting wallet balance for {request.user.username}: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Unable to get wallet balance'
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
