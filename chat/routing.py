from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/home/$', consumers.HomeConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>[\w\-\_\.]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/private_chat/(?P<chat_id>[\w\-\_\.]+)/$', consumers.PrivateChatConsumer.as_asgi()),
]