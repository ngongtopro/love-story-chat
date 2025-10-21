from rest_framework import serializers
from django.utils import timezone
from .models import Farm, CropType, FarmPlot, FarmTransaction


class CropTypeSerializer(serializers.ModelSerializer):
    profit = serializers.ReadOnlyField()
    profit_per_hour = serializers.ReadOnlyField()
    
    class Meta:
        model = CropType
        fields = [
            'id', 'name', 'description', 'emoji', 'seed_price',
            'sell_price', 'growth_time_minutes', 'experience_reward',
            'min_level_required', 'energy_cost', 'profit', 'profit_per_hour'
        ]


class FarmPlotSerializer(serializers.ModelSerializer):
    crop_type = CropTypeSerializer(read_only=True)
    time_until_ready = serializers.SerializerMethodField()
    time_until_withers = serializers.SerializerMethodField()
    
    class Meta:
        model = FarmPlot
        fields = [
            'id', 'plot_number', 'state', 'crop_type',
            'planted_at', 'ready_at', 'withers_at',
            'time_until_ready', 'time_until_withers'
        ]
    
    def get_time_until_ready(self, obj):
        if obj.state != 'planted' or not obj.ready_at:
            return None
        
        time_left = obj.ready_at - timezone.now()
        if time_left.total_seconds() <= 0:
            return 0
        
        return int(time_left.total_seconds())
    
    def get_time_until_withers(self, obj):
        if obj.state != 'ready' or not obj.withers_at:
            return None
        
        time_left = obj.withers_at - timezone.now()
        if time_left.total_seconds() <= 0:
            return 0
        
        return int(time_left.total_seconds())


class FarmSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    plots = FarmPlotSerializer(many=True, read_only=True)
    energy_percentage = serializers.SerializerMethodField()
    experience_to_next_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Farm
        fields = [
            'id', 'user', 'level', 'experience', 'energy',
            'max_energy', 'energy_percentage', 'experience_to_next_level',
            'plots_unlocked', 'created_at', 'updated_at', 'plots'
        ]
        read_only_fields = [
            'id', 'level', 'experience', 'energy', 'max_energy',
            'plots_unlocked', 'created_at', 'updated_at'
        ]
    
    def get_energy_percentage(self, obj):
        if obj.max_energy == 0:
            return 0
        return (obj.energy / obj.max_energy) * 100
    
    def get_experience_to_next_level(self, obj):
        next_level_exp = ((obj.level) ** 2) * 100
        return next_level_exp - obj.experience


class FarmTransactionSerializer(serializers.ModelSerializer):
    crop_type = CropTypeSerializer(read_only=True)
    
    class Meta:
        model = FarmTransaction
        fields = [
            'id', 'transaction_type', 'amount', 'crop_type',
            'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PlantCropSerializer(serializers.Serializer):
    plot_number = serializers.IntegerField(min_value=0, max_value=19)
    crop_type_id = serializers.IntegerField()
    
    def validate_crop_type_id(self, value):
        try:
            crop_type = CropType.objects.get(id=value)
            return crop_type
        except CropType.DoesNotExist:
            raise serializers.ValidationError("Invalid crop type")
    
    def validate(self, attrs):
        user = self.context['request'].user
        plot_number = attrs['plot_number']
        crop_type = attrs['crop_type_id']
        
        # Get farm
        try:
            farm = user.farm
        except Farm.DoesNotExist:
            raise serializers.ValidationError("User does not have a farm")
        
        # Check if plot is unlocked
        if plot_number >= farm.plots_unlocked:
            raise serializers.ValidationError("Plot is not unlocked yet")
        
        # Check if user has required level
        if farm.level < crop_type.min_level_required:
            raise serializers.ValidationError(
                f"Farm level {crop_type.min_level_required} required to plant {crop_type.name}"
            )
        
        # Check if user has enough energy
        if not farm.can_use_energy(crop_type.energy_cost):
            raise serializers.ValidationError("Not enough energy")
        
        # Get or create the plot
        plot, created = FarmPlot.objects.get_or_create(
            farm=farm,
            plot_number=plot_number,
            defaults={'state': 'empty'}
        )
        
        if plot.state != 'empty':
            raise serializers.ValidationError("Plot is not empty")
        
        attrs['farm'] = farm
        attrs['plot'] = plot
        attrs['crop_type'] = crop_type
        
        return attrs


class HarvestPlotSerializer(serializers.Serializer):
    plot_number = serializers.IntegerField(min_value=0, max_value=19)
    
    def validate(self, attrs):
        user = self.context['request'].user
        plot_number = attrs['plot_number']
        
        try:
            farm = user.farm
        except Farm.DoesNotExist:
            raise serializers.ValidationError("User does not have a farm")
        
        try:
            plot = FarmPlot.objects.get(farm=farm, plot_number=plot_number)
        except FarmPlot.DoesNotExist:
            raise serializers.ValidationError("Plot does not exist")
        
        attrs['farm'] = farm
        attrs['plot'] = plot
        
        return attrs


class ClearPlotSerializer(serializers.Serializer):
    plot_number = serializers.IntegerField(min_value=0, max_value=19)
    
    def validate(self, attrs):
        user = self.context['request'].user
        plot_number = attrs['plot_number']
        
        try:
            farm = user.farm
        except Farm.DoesNotExist:
            raise serializers.ValidationError("User does not have a farm")
        
        try:
            plot = FarmPlot.objects.get(farm=farm, plot_number=plot_number)
        except FarmPlot.DoesNotExist:
            raise serializers.ValidationError("Plot does not exist")
        
        attrs['farm'] = farm
        attrs['plot'] = plot
        
        return attrs


class FarmStatsSerializer(serializers.Serializer):
    total_crops_planted = serializers.IntegerField()
    total_crops_harvested = serializers.IntegerField()
    total_money_earned = serializers.IntegerField()
    total_money_spent = serializers.IntegerField()
    total_experience_gained = serializers.IntegerField()
    current_planted_crops = serializers.IntegerField()
    ready_to_harvest = serializers.IntegerField()
    withered_crops = serializers.IntegerField()
    energy_regeneration_time = serializers.IntegerField()  # Minutes until full energy
