"""
Root URL configuration.

Add application routes under ``/api/`` by including their urls module here:

    path("api/v1/", include("apps.myapp.urls")),

https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.core.views import healthz, readyz

urlpatterns = [
    # Operational probes (used by the container healthchecks).
    path("healthz/", healthz, name="healthz"),
    path("readyz/", readyz, name="readyz"),
    # Admin. `/admin/` is a honeypot that logs login attempts; the real admin
    # lives behind ADMIN_URL.
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    path(settings.ADMIN_URL, admin.site.urls),
    # OpenAPI schema and browsable documentation.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# In production nginx serves these directly from the shared volumes.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Backend Service Administration Panel"
admin.site.index_title = "Backend Service"
admin.site.site_title = "Backend Service Admin"
