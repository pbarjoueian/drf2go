"""
RabbitMQ configuration settings.

This module contains RabbitMQ-related settings for Celery message broker.
"""

import re
from urllib.parse import quote, unquote

from django.core.exceptions import ImproperlyConfigured

from ..env import env

# RabbitMQ Configuration
# RabbitMQ connection URL format: amqp://username:password@host:port/vhost
RABBITMQ_URL = env("RABBITMQ_URL", default=None)

# RabbitMQ connection parameters (alternative to RABBITMQ_URL)
RABBITMQ_HOST = env("RABBITMQ_HOST", default="rabbitmq")
RABBITMQ_PORT = env("RABBITMQ_PORT", default=5672, cast=int)
RABBITMQ_USER = env("RABBITMQ_USER", default="guest")
RABBITMQ_PASSWORD = env("RABBITMQ_PASSWORD", default="guest")
RABBITMQ_VHOST = env("RABBITMQ_VHOST", default="/")

# Get DEBUG setting to validate production requirements
DEBUG = env.bool("DEBUG", default=True)


def _parse_rabbitmq_url(url: str) -> dict:
    """
    Parse RabbitMQ AMQP URL into components.

    Args:
        url: RabbitMQ AMQP URL string (format: amqp://user:pass@host:port/vhost)

    Returns:
        Dictionary with host, port, user, password, and vhost keys

    Raises:
        ValueError: If URL format is invalid
    """
    pattern = (
        r"amqp://(?:(?P<user>[^:]+):(?P<password>[^@]+)@)?"
        r"(?P<host>[^:/]+)(?::(?P<port>\d+))?(?:/(?P<vhost>[^/]+))?"
    )
    rabbitmq_match = re.match(pattern, url)
    if not rabbitmq_match:
        raise ValueError(f"Invalid RabbitMQ URL format: {url}")

    result = {
        "host": rabbitmq_match.group("host") or "rabbitmq",
        "port": int(rabbitmq_match.group("port")) if rabbitmq_match.group("port") else 5672,
        "user": rabbitmq_match.group("user") or "guest",
        "password": None,
        "vhost": rabbitmq_match.group("vhost") or "/",
    }

    password = rabbitmq_match.group("password")
    if password:
        # Decode URL-encoded password
        result["password"] = unquote(password)

    return result


def _build_rabbitmq_url(
    host: str,
    port: int,
    user: str = "guest",
    password: str | None = None,
    vhost: str = "/",
) -> str:
    """
    Build RabbitMQ AMQP URL from components.

    Args:
        host: RabbitMQ host
        port: RabbitMQ port
        user: RabbitMQ username
        password: RabbitMQ password (optional)
        vhost: RabbitMQ virtual host

    Returns:
        RabbitMQ AMQP URL string
    """
    password_part = ""
    if password:
        # URL-encode password if it contains special characters
        password_part = f":{quote(password)}"

    # URL-encode vhost if it contains special characters
    encoded_vhost = quote(vhost, safe="")

    return f"amqp://{user}{password_part}@{host}:{port}/{encoded_vhost}"


# Parse RabbitMQ URL if provided, otherwise use individual parameters
if RABBITMQ_URL:
    try:
        parsed = _parse_rabbitmq_url(RABBITMQ_URL)
        RABBITMQ_HOST = parsed["host"]
        RABBITMQ_PORT = parsed["port"]
        RABBITMQ_USER = parsed["user"]
        RABBITMQ_PASSWORD = parsed["password"] or "guest"
        RABBITMQ_VHOST = parsed["vhost"]
    except ValueError:
        # If URL parsing fails, fall back to individual parameters
        # and reconstruct URL
        RABBITMQ_URL = _build_rabbitmq_url(
            RABBITMQ_HOST,
            RABBITMQ_PORT,
            RABBITMQ_USER,
            RABBITMQ_PASSWORD,
            RABBITMQ_VHOST,
        )
else:
    # Use individual parameters if RABBITMQ_URL is not set
    RABBITMQ_URL = _build_rabbitmq_url(
        RABBITMQ_HOST,
        RABBITMQ_PORT,
        RABBITMQ_USER,
        RABBITMQ_PASSWORD,
        RABBITMQ_VHOST,
    )

# Validate production requirements
if not DEBUG and RABBITMQ_PASSWORD == "guest":
    raise ImproperlyConfigured(
        "RABBITMQ_PASSWORD must be changed from default 'guest' in production. "
        "Set RABBITMQ_PASSWORD environment variable "
        "or include it in RABBITMQ_URL."
    )

