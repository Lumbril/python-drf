from apps.chat.consumers import ChatConsumer
from apps.chat.views import room, event

from django.urls import path, re_path


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<guild_id>\w+)/$', ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('<int:guild_id>', room),
    path('sender', event)
]
