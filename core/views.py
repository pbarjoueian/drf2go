"""
Operational endpoints.

`/healthz/` is a liveness probe: it answers as long as the ASGI application is
serving, and is what the container healthchecks use. `/readyz/` is a readiness
probe that additionally verifies the backing services, so a load balancer can
avoid routing traffic to an instance whose database or channel layer is down.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import connections
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def healthz(request):
    """Liveness probe - no external dependencies are touched."""
    return JsonResponse({"status": "ok"})


@never_cache
@require_GET
def readyz(request):
    """Readiness probe - verifies the database and the channel layer."""
    checks = {}

    try:
        connections["default"].ensure_connection()
    except Exception as exc:
        checks["database"] = f"error: {exc}"
    else:
        checks["database"] = "ok"

    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            checks["channel_layer"] = "not configured"
        else:
            async_to_sync(channel_layer.send)(
                "healthcheck", {"type": "healthcheck.ping"}
            )
            checks["channel_layer"] = "ok"
    except Exception as exc:
        checks["channel_layer"] = f"error: {exc}"

    healthy = all(value == "ok" for value in checks.values())
    return JsonResponse(
        {"status": "ok" if healthy else "degraded", "checks": checks},
        status=200 if healthy else 503,
    )
