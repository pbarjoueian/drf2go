"""
AppConfig overrides for third-party apps.

``DEFAULT_AUTO_FIELD = BigAutoField`` applies to every installed app, including
ones whose shipped migrations were written against ``AutoField``. Without an
override Django reports permanent "changes not yet reflected in a migration"
drift for those apps and would want a migration inside site-packages.

Pinning the auto field per app keeps the project default at BigAutoField for our
own models while leaving vendored schemas alone.
"""

from django.apps import AppConfig


class AdminHoneypotConfig(AppConfig):
    """django-admin-honeypot1 ships AutoField-based migrations."""

    name = "admin_honeypot"
    label = "admin_honeypot"
    verbose_name = "Admin Honeypot"
    default_auto_field = "django.db.models.AutoField"
