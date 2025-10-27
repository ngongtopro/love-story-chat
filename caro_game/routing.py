from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/caro/rooms/$', consumers.CaroRoomListConsumer.as_asgi()),
    re_path(r'ws/caro/game/(?P<room_name>[^/]+)/$', consumers.CaroGameConsumer.as_asgi()),
]
