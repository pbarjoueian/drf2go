"""
Redis configuration settings.

This module contains Redis-related settings for caching and Channels.
"""

import re
from urllib.parse import quote, unquote

from django.core.exceptions import ImproperlyConfigured

from ..env import env

# Redis Configuration
# Redis connection URL format: redis://host:port
# or redis://password@host:port
REDIS_URL = env("REDIS_URL", default=None)

# Redis connection parameters (alternative to REDIS_URL)
REDIS_HOST = env("REDIS_HOST", default="redis")
REDIS_PORT = env("REDIS_PORT", default=6379, cast=int)
REDIS_PASSWORD = env("REDIS_PASSWORD", default=None)
REDIS_DB = env("REDIS_DB", default=0, cast=int)

# Get DEBUG setting to validate production requirements
DEBUG = env.bool("DEBUG", default=True)


def _parse_redis_url(url: str) -> dict:
    """
    Parse Redis URL into components.

    Args:
        url: Redis URL string

    Returns:
        Dictionary with host, port, password, and db keys

    Raises:
        ValueError: If URL format is invalid
    """
    pattern = (
        r"redis://(?:(?P<password>[^@]+)@)?"
        r"(?P<host>[^:]+):(?P<port>\d+)(?:/(?P<db>\d+))?"
    )
    redis_match = re.match(pattern, url)
    if not redis_match:
        raise ValueError(f"Invalid Redis URL format: {url}")

    result = {
        "host": redis_match.group("host"),
        "port": int(redis_match.group("port")),
        "password": None,
        "db": 0,
    }

    password = redis_match.group("password")
    if password:
        # Decode URL-encoded password
        result["password"] = unquote(password)

    db = redis_match.group("db")
    if db:
        result["db"] = int(db)

    return result


def _build_redis_url(
    host: str, port: int, password: str | None = None, db: int = 0
) -> str:
    """
    Build Redis URL from components.

    Args:
        host: Redis host
        port: Redis port
        password: Redis password (optional)
        db: Redis database number

    Returns:
        Redis URL string
    """
    password_part = ""
    if password:
        # URL-encode password if it contains special characters
        password_part = f"{quote(password)}@"

    return f"redis://{password_part}{host}:{port}/{db}"


# Parse Redis URL if provided, otherwise use individual parameters
if REDIS_URL:
    try:
        parsed = _parse_redis_url(REDIS_URL)
        REDIS_HOST = parsed["host"]
        REDIS_PORT = parsed["port"]
        REDIS_PASSWORD = parsed["password"]
        REDIS_DB = parsed["db"]
    except ValueError:
        # If URL parsing fails, fall back to individual parameters
        # and reconstruct URL
        REDIS_URL = _build_redis_url(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB)
else:
    # Use individual parameters if REDIS_URL is not set
    REDIS_URL = _build_redis_url(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB)

# Validate production requirements
if not DEBUG and not REDIS_PASSWORD:
    raise ImproperlyConfigured(
        "REDIS_PASSWORD is required in production. "
        "Set REDIS_PASSWORD environment variable "
        "or include it in REDIS_URL."
    )

# Redis configuration dictionary for Channels
# channels-redis format: hosts can be tuples or connection strings
if REDIS_PASSWORD:
    # Use connection string format with password
    redis_connection_string = (
        f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )
    REDIS_CONFIG = {
        "hosts": [redis_connection_string],
    }
else:
    # No password - use tuple format
    REDIS_CONFIG = {
        "hosts": [(REDIS_HOST, REDIS_PORT)],
    }
    if REDIS_DB != 0:
        REDIS_CONFIG["db"] = REDIS_DB
