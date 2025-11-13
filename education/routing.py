from typing import Any, cast
from django.urls import re_path
from .consumers import MeetingConsumer


websocket_urlpatterns: list[Any] = [
    # Cast to Any to satisfy typing: Channels URLRouter accepts ASGI apps here
    re_path(r"^ws/meetings/(?P<room_name>[^/]+)/$", cast(Any, MeetingConsumer.as_asgi())),
]
