from django.urls import path
from . import views

app_name = 'caro_game'

urlpatterns = [
    # Private Chat Caro Game URLs
    path('private/create/', views.create_private_caro_game, name='create_private_caro_game'),
    path('private/join/<str:room_code>/', views.join_private_caro_game, name='join_private_caro_game'), 
    path('private/move/', views.make_private_caro_move, name='make_private_caro_move'),
    path('private/status/<str:room_code>/', views.get_private_caro_game, name='get_private_caro_game'),
    path('private/abandon/<str:room_code>/', views.abandon_private_caro_game, name='abandon_private_caro_game'),
    
    # Room Caro Game URLs (Legacy)
    path('rooms/', views.list_caro_rooms, name='list_caro_rooms'),
    path('room/create/', views.create_room_caro_game, name='create_room_caro_game'),
    path('room/<str:room_name>/', views.caro_game_room, name='caro_game_room'),
    path('room/join/<str:room_name>/', views.join_room_caro_game, name='join_room_caro_game'),
    path('room/move/', views.make_room_caro_move, name='make_room_caro_move'),
    path('room/abandon/<str:room_name>/', views.abandon_room_caro_game, name='abandon_room_caro_game'),
    
    # Game Statistics URLs
    path('api/stats/', views.get_game_stats, name='get_game_stats'),
    path('api/test/', views.api_test, name='api_test'),
    
    # API endpoints for room-based games
    path('api/<str:room_name>/status/', views.get_room_game_status, name='get_room_game_status'),
    path('<str:room_name>/status/', views.get_room_game_status, name='get_room_game_status_alt'),
    path('<str:room_name>/move/', views.make_room_caro_move, name='make_room_caro_move_alt'),
    path('<str:room_name>/create/', views.create_room_caro_game, name='create_room_caro_game_alt'),
    path('<str:room_name>/join/', views.join_room_caro_game, name='join_room_caro_game_alt'),
    path('<str:room_name>/abandon/', views.abandon_room_caro_game, name='abandon_room_caro_game_alt'),
]
