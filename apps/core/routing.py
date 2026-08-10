"""
WebSocket URL routing configuration.

This module defines WebSocket URL patterns.
"""

from django.urls import path

from apps.core.consumers import SimpleConsumer

websocket_urlpatterns = [
    path("ws/simple/", SimpleConsumer.as_asgi()),
]
