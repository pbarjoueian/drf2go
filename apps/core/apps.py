"""
App configuration for the `core` app.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Shared utilities, Celery tasks and WebSocket consumers."""

    default_auto_field = "django.db.models.BigAutoField"
    # Dotted import path; the app label stays the trailing component ("core").
    name = "apps.core"
    verbose_name = "Core"
