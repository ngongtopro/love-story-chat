from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Room
from user_wallet.models import Wallet
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Create wallet for new users"""
    if created:
        wallet = Wallet.objects.create(
            user=instance,
            balance=100000  # Start with 100,000 đồng
        )
        
        # Create initial transaction record
        from user_wallet.models import WalletTransaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='initial',
            amount=100000,
            balance_after=100000,
            description='Welcome bonus - Initial balance'
        )
        
        logger.info(f"Wallet created for user {instance.username} with 100,000 đồng")


@receiver(post_save, sender=User)
def create_user_farm(sender, instance, created, **kwargs):
    """Create farm for new users"""
    if created:
        from happy_farm.models import Farm, FarmPlot
        
        # Create farm
        farm = Farm.objects.create(
            user=instance,
            level=1,
            experience=0,
            energy=100,
            plots_unlocked=6
        )
        
        # Create initial plots
        for plot_number in range(farm.plots_unlocked):
            FarmPlot.objects.create(
                farm=farm,
                plot_number=plot_number,
                state='empty'
            )
        
        logger.info(f"Farm created for user {instance.username} with {farm.plots_unlocked} plots")


@receiver(post_save, sender=Room)
def room_created_signal(sender, instance, created, **kwargs):
    """Send real-time notification when room is created or updated"""
    channel_layer = get_channel_layer()
    
    if channel_layer:
        try:
            room_data = {
                'id': instance.id,
                'name': instance.name,
                'description': instance.description or '',
                'created_by': instance.created_by.username,
                'created_at': instance.created_at.strftime('%B %d, %Y'),
                'created_at_iso': instance.created_at.isoformat(),
            }
            
            if created:
                # Room was just created
                async_to_sync(channel_layer.group_send)(
                    'home_updates',
                    {
                        'type': 'room_created',
                        'room': room_data
                    }
                )
                logger.info(f"Room created signal sent: {instance.name}")
            else:
                # Room was updated
                async_to_sync(channel_layer.group_send)(
                    'home_updates',
                    {
                        'type': 'room_updated',
                        'room': room_data
                    }
                )
                logger.info(f"Room updated signal sent: {instance.name}")
                
        except Exception as e:
            logger.error(f"Error sending room signal: {e}")
    else:
        logger.warning("Channel layer not available for room signals")