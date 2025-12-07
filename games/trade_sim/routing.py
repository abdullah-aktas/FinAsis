"""
TradeSim WebSocket routing configuration
"""
from django.urls import re_path  # type: ignore
from . import consumers

# WebSocket URL patterns for Django Channels
websocket_urlpatterns = [
    re_path(r"^ws/game/$", consumers.GameConsumer.as_asgi()),  # type: ignore
    re_path(r"^ws/notifications/$", consumers.NotificationConsumer.as_asgi()),  # type: ignore
]
