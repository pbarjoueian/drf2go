"""
WSGI entrypoint.

Only serves HTTP - WebSockets require the ASGI application in ``config.asgi``,
which is what the Docker images run. This module exists for WSGI-only tooling.

https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
