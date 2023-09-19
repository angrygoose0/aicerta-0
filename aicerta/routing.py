from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from main import consumers

websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]
