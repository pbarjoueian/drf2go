"""
Tests for the shared `apps.core` app.

These pin the `apps/` package layout: an app moved out of it, or registered
under its bare name, fails here rather than at container start.
"""

from django.apps import apps as django_apps

from apps.core.routing import websocket_urlpatterns


def test_core_app_is_installed_from_the_apps_package():
    """`apps.core` is importable under that dotted path and keeps its label."""
    app_config = django_apps.get_app_config("core")
    assert app_config.name == "apps.core"


def test_websocket_routes_are_registered():
    """The consumer import chain used by `config.asgi` resolves."""
    assert websocket_urlpatterns


def test_healthz_is_reachable(client):
    """The liveness probe answers without touching external services."""
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
