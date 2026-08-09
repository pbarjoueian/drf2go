"""
CORS configuration (django-cors-headers).
"""

from ..env import env

# Defaults to off. Turning it on in production disables origin checks entirely.
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOWED_ORIGIN_REGEXES = env.list("CORS_ALLOWED_ORIGIN_REGEXES", default=[])
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", default=False)
CORS_ALLOW_METHODS = env.list(
    "CORS_ALLOW_METHODS",
    default=["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
)
