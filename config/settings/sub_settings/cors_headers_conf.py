from ..env import env

CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)
CORS_ALLOW_METHODS = env.list(
    "CORS_ALLOW_METHODS", default=["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])
