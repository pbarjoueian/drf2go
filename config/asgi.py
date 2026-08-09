"""
ASGI entrypoint.

Serves HTTP through Django and WebSockets through Channels.

https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# The app registry must be populated before importing anything that touches
# models, so the HTTP application is built first.
django_asgi_app = get_asgi_application()

from core.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # Browser clients should additionally be guarded with
        # channels.security.websocket.AllowedHostsOriginValidator; it is left
        # off here because it rejects clients that send no Origin header.
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
