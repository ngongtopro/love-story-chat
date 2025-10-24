from django.contrib import admin
from .models import CaroGame, CaroMove


@admin.register(CaroGame)
class CaroGameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'game_type', 'player1', 'player2', 'status', 'winner', 'bet_amount', 'created_at']
    list_filter = ['game_type', 'status', 'created_at', 'bet_amount']
    search_fields = ['game_id', 'chat_id', 'player1__username', 'player2__username']
    readonly_fields = ['game_id', 'total_pot', 'winner_prize', 'house_fee', 'created_at', 'updated_at', 'game_duration']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('player1', 'player2', 'winner')


@admin.register(CaroMove)
class CaroMoveAdmin(admin.ModelAdmin):
    list_display = ['game', 'move_number', 'player', 'symbol', 'row', 'col', 'timestamp']
    list_filter = ['symbol', 'timestamp']
    search_fields = ['game__game_id', 'player__username']
    readonly_fields = ['timestamp']
    ordering = ['game', 'move_number']



