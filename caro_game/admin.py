from django.contrib import admin
from .models import CaroGame, RoomCaroGame


@admin.register(CaroGame)
class CaroGameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'player1', 'player2', 'status', 'winner', 'created_at']
    list_filter = ['status', 'created_at', 'board_size']
    search_fields = ['game_id', 'chat_id', 'player1__username', 'player2__username']
    readonly_fields = ['game_id', 'created_at', 'updated_at', 'game_duration']
    ordering = ['-created_at']


@admin.register(RoomCaroGame)
class RoomCaroGameAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'room_name', 'player1', 'player2', 'status', 'winner', 'bet_amount', 'created_at']
    list_filter = ['status', 'created_at', 'room_name', 'bet_amount']
    search_fields = ['game_id', 'room_name', 'player1__username', 'player2__username']
    readonly_fields = ['game_id', 'total_pot', 'winner_prize', 'house_fee', 'created_at', 'updated_at', 'game_duration']
    ordering = ['-created_at']



