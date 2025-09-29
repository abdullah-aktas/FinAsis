"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

# WebSocket için basit bir consumer (örnek)
from channels.generic.websocket import AsyncWebsocketConsumer  # placeholder for future consumers
import json

# Normalized settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings')

websocket_urlpatterns: list = []  # Add websocket patterns here, e.g., re_path(r"^ws/test/$", Consumer.as_asgi())

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
