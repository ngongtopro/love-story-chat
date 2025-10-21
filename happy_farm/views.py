"""
Farm Game Views for Love Chat
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Farm, CropType, FarmPlot, FarmTransaction
from user_wallet.models import Wallet, WalletTransaction
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def farm_view(request):
    """Main farm view"""
    try:
        # Get or create user's farm
        farm, created = Farm.objects.get_or_create(
            user=request.user,
            defaults={
                'level': 1,
                'experience': 0,
                'energy': 100,
                'plots_unlocked': 6
            }
        )
        
        # Create plots if they don't exist
        existing_plots = farm.plots.count()
        if existing_plots < farm.plots_unlocked:
            for plot_number in range(existing_plots, farm.plots_unlocked):
                FarmPlot.objects.create(
                    farm=farm,
                    plot_number=plot_number,
                    state='empty'
                )
        
        # Update farm state
        farm.update_energy()
        
        # Get all plots and update their states
        plots = farm.plots.all().order_by('plot_number')
        for plot in plots:
            plot.update_state()
        
        # Get available crop types for this level
        available_crops = CropType.objects.filter(min_level_required__lte=farm.level)
        
        # Get recent transactions
        recent_transactions = FarmTransaction.objects.filter(farm=farm)[:10]
        
        context = {
            'farm': farm,
            'plots': plots,
            'available_crops': available_crops,
            'recent_transactions': recent_transactions,
            'wallet': request.user.wallet,
        }
        
        return render(request, 'happy_farm/farm_base.html', context)
        
    except Exception as e:
        logger.error(f"Error loading farm for user {request.user.username}: {e}")
        return render(request, 'happy_farm/farm_base.html', {
            'error': 'Unable to load farm. Please try again later.'
        })


@login_required
@csrf_exempt
def plant_crop_api(request):
    """API endpoint to plant a crop"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        plot_id = data.get('plot_id')
        crop_type_id = data.get('crop_type_id')
        
        if not plot_id or not crop_type_id:
            return JsonResponse({'error': 'Missing plot_id or crop_type_id'}, status=400)
        
        # Get user's plot
        plot = get_object_or_404(FarmPlot, id=plot_id, farm__user=request.user)
        
        # Get crop type
        crop_type = get_object_or_404(CropType, id=crop_type_id)
        
        # Check if user's farm level is high enough
        if plot.farm.level < crop_type.min_level_required:
            return JsonResponse({
                'error': f'Farm level {crop_type.min_level_required} required to plant {crop_type.name}'
            }, status=400)
        
        # Check if user has enough money for seeds
        wallet = request.user.wallet
        if not wallet.has_sufficient_balance(crop_type.seed_price):
            return JsonResponse({
                'error': f'Not enough money. Need {crop_type.seed_price:,} đồng for seeds.',
                'required': crop_type.seed_price,
                'current': wallet.balance
            }, status=400)
        
        # Plant the crop
        success, message = plot.plant_crop(crop_type)
        
        if success:
            # Deduct seed cost from wallet
            wallet.deduct_balance(
                crop_type.seed_price,
                'farm_seeds',
                f'Bought {crop_type.name} seeds'
            )
            
            # Record transaction
            FarmTransaction.objects.create(
                farm=plot.farm,
                transaction_type='seed_purchase',
                amount=-crop_type.seed_price,
                crop_type=crop_type,
                description=f'Planted {crop_type.name} in plot {plot.plot_number}'
            )
            
            # Update farm energy
            plot.farm.update_energy()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully planted {crop_type.emoji} {crop_type.name}!',
                'plot': {
                    'id': plot.id,
                    'state': plot.state,
                    'crop_name': crop_type.name,
                    'crop_emoji': crop_type.emoji,
                    'ready_at': plot.ready_at.isoformat() if plot.ready_at else None,
                },
                'farm': {
                    'energy': plot.farm.energy,
                    'max_energy': plot.farm.max_energy,
                },
                'wallet_balance': wallet.balance,
            })
        else:
            return JsonResponse({'error': message}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error planting crop for user {request.user.username}: {e}")
        return JsonResponse({'error': 'Failed to plant crop'}, status=500)


@login_required
@csrf_exempt
def harvest_crop_api(request):
    """API endpoint to harvest a crop"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        plot_id = data.get('plot_id')
        
        if not plot_id:
            return JsonResponse({'error': 'Missing plot_id'}, status=400)
        
        # Get user's plot
        plot = get_object_or_404(FarmPlot, id=plot_id, farm__user=request.user)
        
        # Harvest the crop
        success, message, money_earned, experience_gained = plot.harvest()
        
        if success:
            # Record transaction
            if plot.crop_type and money_earned > 0:
                FarmTransaction.objects.create(
                    farm=plot.farm,
                    transaction_type='crop_harvest',
                    amount=money_earned,
                    crop_type=plot.crop_type,
                    description=f'Harvested {plot.crop_type.name} from plot {plot.plot_number}'
                )
            
            return JsonResponse({
                'success': True,
                'message': message,
                'money_earned': money_earned,
                'experience_gained': experience_gained,
                'plot': {
                    'id': plot.id,
                    'state': plot.state,
                },
                'farm': {
                    'level': plot.farm.level,
                    'experience': plot.farm.experience,
                    'energy': plot.farm.energy,
                },
                'wallet_balance': request.user.wallet.balance,
            })
        else:
            return JsonResponse({'error': message}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error harvesting crop for user {request.user.username}: {e}")
        return JsonResponse({'error': 'Failed to harvest crop'}, status=500)


@login_required
@csrf_exempt  
def clear_plot_api(request):
    """API endpoint to clear a plot (remove withered crops)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        plot_id = data.get('plot_id')
        
        if not plot_id:
            return JsonResponse({'error': 'Missing plot_id'}, status=400)
        
        # Get user's plot
        plot = get_object_or_404(FarmPlot, id=plot_id, farm__user=request.user)
        
        # Clear the plot
        plot.clear_plot()
        
        return JsonResponse({
            'success': True,
            'message': 'Plot cleared successfully',
            'plot': {
                'id': plot.id,
                'state': plot.state,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error clearing plot for user {request.user.username}: {e}")
        return JsonResponse({'error': 'Failed to clear plot'}, status=500)


@login_required
def farm_status_api(request):
    """API endpoint to get current farm status"""
    try:
        farm = request.user.farm
        farm.update_energy()
        
        # Update all plot states
        plots_data = []
        for plot in farm.plots.all().order_by('plot_number'):
            plot.update_state()
            plot_data = {
                'id': plot.id,
                'plot_number': plot.plot_number,
                'state': plot.state,
                'crop_name': plot.crop_type.name if plot.crop_type else None,
                'crop_emoji': plot.crop_type.emoji if plot.crop_type else None,
                'planted_at': plot.planted_at.isoformat() if plot.planted_at else None,
                'ready_at': plot.ready_at.isoformat() if plot.ready_at else None,
                'withers_at': plot.withers_at.isoformat() if plot.withers_at else None,
                'time_until_ready': None
            }
            
            if plot.time_until_ready:
                total_seconds = int(plot.time_until_ready.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                plot_data['time_until_ready'] = f"{hours}h {minutes}m"
            
            plots_data.append(plot_data)
        
        return JsonResponse({
            'success': True,
            'farm': {
                'level': farm.level,
                'experience': farm.experience,
                'energy': farm.energy,
                'max_energy': farm.max_energy,
                'plots_unlocked': farm.plots_unlocked,
            },
            'plots': plots_data,
            'wallet_balance': request.user.wallet.balance,
        })
        
    except Exception as e:
        logger.error(f"Error getting farm status for user {request.user.username}: {e}")
        return JsonResponse({'error': 'Failed to get farm status'}, status=500)