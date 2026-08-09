"""
The project's settings package.

``config.settings`` is the single canonical value for ``DJANGO_SETTINGS_MODULE``
- manage.py, wsgi.py, asgi.py, Celery, pytest and the compose files all point
here. Import from ``config.settings``, never from ``config.settings.base``.
"""

from .base import *
