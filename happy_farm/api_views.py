from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Sum, Count
from django.utils import timezone

from .models import Farm, CropType, FarmPlot, FarmTransaction
from .serializers import (
    FarmSerializer, CropTypeSerializer, FarmPlotSerializer,
    FarmTransactionSerializer, PlantCropSerializer,
    HarvestPlotSerializer, ClearPlotSerializer, FarmStatsSerializer
)


class CropTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for crop types
    """
    queryset = CropType.objects.all().order_by('min_level_required', 'growth_time_minutes')
    serializer_class = CropTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['min_level_required']
    ordering_fields = ['seed_price', 'sell_price', 'growth_time_minutes', 'min_level_required']

    def get_queryset(self):
        """Filter crops by user's farm level"""
        user = self.request.user
        try:
            farm = user.farm
            return super().get_queryset().filter(min_level_required__lte=farm.level)
        except Farm.DoesNotExist:
            return super().get_queryset().filter(min_level_required__lte=1)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get crops available for user's current level"""
        user = request.user
        try:
            farm = user.farm
            crops = CropType.objects.filter(min_level_required__lte=farm.level)
        except Farm.DoesNotExist:
            crops = CropType.objects.filter(min_level_required__lte=1)
        
        serializer = self.get_serializer(crops, many=True)
        return Response(serializer.data)


class FarmViewSet(viewsets.ModelViewSet):
    """
    ViewSet for farms
    """
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Farm.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create user's farm"""
        farm, created = Farm.objects.get_or_create(
            user=self.request.user,
            defaults={
                'level': 1,
                'experience': 0,
                'energy': 100,
                'max_energy': 100,
                'plots_unlocked': 6
            }
        )
        
        # Create initial plots
        if created:
            for i in range(farm.plots_unlocked):
                FarmPlot.objects.get_or_create(
                    farm=farm,
                    plot_number=i,
                    defaults={'state': 'empty'}
                )
        
        return farm

    @action(detail=False, methods=['get'])
    def my_farm(self, request):
        """Get current user's farm"""
        farm = self.get_object()
        farm.update_energy()  # Update energy before returning
        
        # Update all plot states
        for plot in farm.plots.all():
            plot.update_state()
        
        serializer = self.get_serializer(farm)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def plant_crop(self, request):
        """Plant a crop in a plot"""
        serializer = PlantCropSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        plot = serializer.validated_data['plot']
        crop_type = serializer.validated_data['crop_type']
        
        success, message = plot.plant_crop(crop_type)
        
        if success:
            # Create transaction record
            FarmTransaction.objects.create(
                farm=plot.farm,
                transaction_type='seed_purchase',
                amount=-crop_type.seed_price,
                crop_type=crop_type,
                description=f'Planted {crop_type.name} in plot {plot.plot_number}'
            )
            
            return Response({
                'success': True,
                'message': message,
                'plot': FarmPlotSerializer(plot).data
            })
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def harvest_plot(self, request):
        """Harvest a plot"""
        serializer = HarvestPlotSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        plot = serializer.validated_data['plot']
        
        success, message, money_earned, experience_gained = plot.harvest()
        
        if success:
            # Create transaction record
            if money_earned > 0 and plot.crop_type:
                FarmTransaction.objects.create(
                    farm=plot.farm,
                    transaction_type='crop_harvest',
                    amount=money_earned,
                    crop_type=plot.crop_type,
                    description=f'Harvested {plot.crop_type.name} from plot {plot.plot_number}'
                )
            
            return Response({
                'success': True,
                'message': message,
                'money_earned': money_earned,
                'experience_gained': experience_gained,
                'plot': FarmPlotSerializer(plot).data
            })
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def clear_plot(self, request):
        """Clear a withered or unwanted plot"""
        serializer = ClearPlotSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        plot = serializer.validated_data['plot']
        
        if plot.state in ['withered', 'planted', 'ready']:
            plot.clear_plot()
            return Response({
                'success': True,
                'message': f'Plot {plot.plot_number} cleared',
                'plot': FarmPlotSerializer(plot).data
            })
        else:
            return Response({
                'success': False,
                'message': 'Plot is already empty'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def harvest_all(self, request):
        """Harvest all ready plots"""
        farm = self.get_object()
        farm.update_energy()
        
        ready_plots = farm.plots.filter(state='ready')
        
        if not ready_plots.exists():
            return Response({
                'success': False,
                'message': 'No plots ready for harvest'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        total_money = 0
        total_experience = 0
        harvested_crops = []
        
        for plot in ready_plots:
            success, message, money_earned, experience_gained = plot.harvest()
            if success:
                total_money += money_earned
                total_experience += experience_gained
                harvested_crops.append({
                    'plot_number': plot.plot_number,
                    'money_earned': money_earned,
                    'experience_gained': experience_gained
                })
        
        return Response({
            'success': True,
            'message': f'Harvested {len(harvested_crops)} plots',
            'total_money': total_money,
            'total_experience': total_experience,
            'harvested_crops': harvested_crops
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get farm statistics"""
        farm = self.get_object()
        transactions = farm.transactions.all()
        
        # Calculate stats
        total_planted = transactions.filter(transaction_type='seed_purchase').count()
        total_harvested = transactions.filter(transaction_type='crop_harvest').count()
        
        money_earned = transactions.filter(
            transaction_type='crop_harvest'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        money_spent = abs(transactions.filter(
            transaction_type='seed_purchase'
        ).aggregate(Sum('amount'))['amount__sum'] or 0)
        
        # Current plot states
        current_planted = farm.plots.filter(state='planted').count()
        ready_to_harvest = farm.plots.filter(state='ready').count()
        withered_crops = farm.plots.filter(state='withered').count()
        
        # Energy regeneration time
        energy_needed = farm.max_energy - farm.energy
        energy_regen_time = energy_needed * 5  # 5 minutes per energy point
        
        stats_data = {
            'total_crops_planted': total_planted,
            'total_crops_harvested': total_harvested,
            'total_money_earned': money_earned,
            'total_money_spent': money_spent,
            'total_experience_gained': farm.experience,
            'current_planted_crops': current_planted,
            'ready_to_harvest': ready_to_harvest,
            'withered_crops': withered_crops,
            'energy_regeneration_time': energy_regen_time
        }
        
        serializer = FarmStatsSerializer(stats_data)
        return Response(serializer.data)


class FarmTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for farm transactions
    """
    serializer_class = FarmTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['transaction_type']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        try:
            farm = user.farm
            return FarmTransaction.objects.filter(farm=farm)
        except Farm.DoesNotExist:
            return FarmTransaction.objects.none()

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
