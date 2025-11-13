from __future__ import annotations

import os
from typing import Iterable

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()


def _collect_websocket_patterns() -> list:
    patterns: list = []
    sources: Iterable[tuple[str, str]] = (
        ('education.routing', 'websocket_urlpatterns'),
        ('games.routing', 'websocket_urlpatterns'),
        ('games.trade_sim.routing', 'websocket_urlpatterns'),
    )
    for module_path, attr in sources:
        try:
            module = __import__(module_path, fromlist=[attr])
            patterns.extend(getattr(module, attr, []))
        except Exception:
            continue
    return patterns


application = ProtocolTypeRouter(
    {
        'http': django_asgi_app,
        'websocket': AuthMiddlewareStack(URLRouter(_collect_websocket_patterns())),
    }
)

