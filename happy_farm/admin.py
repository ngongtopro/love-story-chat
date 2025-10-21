from django.contrib import admin
from .models import Farm, CropType, FarmPlot, FarmTransaction


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'experience', 'energy', 'max_energy', 'plots_unlocked', 'created_at']
    list_filter = ['level', 'created_at', 'plots_unlocked']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'last_energy_update']
    ordering = ['-level', '-experience']


@admin.register(CropType)
class CropTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'seed_price', 'sell_price', 'profit', 'growth_time_minutes', 'min_level_required']
    list_filter = ['min_level_required', 'growth_time_minutes']
    search_fields = ['name', 'description']
    ordering = ['min_level_required', 'growth_time_minutes']
    
    def profit(self, obj):
        return obj.profit
    profit.short_description = 'Profit'


@admin.register(FarmPlot)
class FarmPlotAdmin(admin.ModelAdmin):
    list_display = ['farm_user', 'plot_number', 'state', 'crop_type', 'planted_at', 'ready_at']
    list_filter = ['state', 'planted_at', 'ready_at']
    search_fields = ['farm__user__username', 'crop_type__name']
    readonly_fields = ['planted_at', 'ready_at', 'withers_at']
    ordering = ['farm', 'plot_number']
    
    def farm_user(self, obj):
        return obj.farm.user.username
    farm_user.short_description = 'Farm User'


@admin.register(FarmTransaction)
class FarmTransactionAdmin(admin.ModelAdmin):
    list_display = ['farm_user', 'transaction_type', 'amount', 'crop_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['farm__user__username', 'description', 'crop_type__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def farm_user(self, obj):
        return obj.farm.user.username
    farm_user.short_description = 'Farm User'
