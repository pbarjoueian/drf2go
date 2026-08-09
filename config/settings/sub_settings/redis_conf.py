"""
Redis configuration.

Redis backs the Channels layer (and is available for caching). The connection
can be given either as a single ``REDIS_URL`` or as discrete ``REDIS_*``
parameters; whichever is supplied, both a normalised URL and the individual
components are exported so downstream modules never have to re-parse anything.
"""

from django.core.exceptions import ImproperlyConfigured

from ..env import env
from .url_utils import build_url, parse_url

REDIS_URL = env("REDIS_URL", default="")
REDIS_HOST = env("REDIS_HOST", default="redis")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_USER = env("REDIS_USER", default="")
REDIS_PASSWORD = env("REDIS_PASSWORD", default="") or None
REDIS_DB = env.int("REDIS_DB", default=0)

DEBUG = env.bool("DEBUG", default=True)

if REDIS_URL:
    parts = parse_url(REDIS_URL, default_port=6379, default_host="redis")
    REDIS_HOST = parts.host
    REDIS_PORT = parts.port
    REDIS_USER = parts.username or ""
    REDIS_PASSWORD = parts.password
    REDIS_DB = int(parts.path.strip("/") or 0)

REDIS_URL = build_url(
    scheme="redis",
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USER or None,
    password=REDIS_PASSWORD,
    path=f"/{REDIS_DB}",
)

if not DEBUG and not REDIS_PASSWORD:
    raise ImproperlyConfigured(
        "REDIS_PASSWORD is required when DEBUG is off. Set REDIS_PASSWORD or "
        "include the password in REDIS_URL."
    )

# channels-redis accepts a connection URL directly.
REDIS_CONFIG = {"hosts": [REDIS_URL]}
