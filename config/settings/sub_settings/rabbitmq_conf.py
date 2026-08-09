"""
RabbitMQ configuration.

RabbitMQ is the Celery broker. As with Redis, the connection may be supplied as
a single ``RABBITMQ_URL`` or as discrete ``RABBITMQ_*`` parameters, and both
forms are normalised into ``RABBITMQ_URL`` plus individual components.
"""

from django.core.exceptions import ImproperlyConfigured

from ..env import env
from .url_utils import build_url, parse_url

RABBITMQ_URL = env("RABBITMQ_URL", default="")
RABBITMQ_HOST = env("RABBITMQ_HOST", default="rabbitmq")
RABBITMQ_PORT = env.int("RABBITMQ_PORT", default=5672)
RABBITMQ_USER = env("RABBITMQ_USER", default="guest")
RABBITMQ_PASSWORD = env("RABBITMQ_PASSWORD", default="guest")
# The default vhost is "/", which is written as an empty path in an AMQP URL.
RABBITMQ_VHOST = env("RABBITMQ_VHOST", default="/")

DEBUG = env.bool("DEBUG", default=True)

if RABBITMQ_URL:
    parts = parse_url(RABBITMQ_URL, default_port=5672, default_host="rabbitmq")
    RABBITMQ_HOST = parts.host
    RABBITMQ_PORT = parts.port
    RABBITMQ_USER = parts.username or "guest"
    RABBITMQ_PASSWORD = parts.password or "guest"
    RABBITMQ_VHOST = parts.path.lstrip("/") or "/"

# An AMQP URL carries the vhost as the path, so the default vhost "/" is
# written as a doubled slash: amqp://user:pass@host:5672//
RABBITMQ_URL = build_url(
    scheme="amqp",
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    username=RABBITMQ_USER,
    password=RABBITMQ_PASSWORD,
    path=f"/{RABBITMQ_VHOST}",
)

if not DEBUG and RABBITMQ_PASSWORD == "guest":
    raise ImproperlyConfigured(
        "RABBITMQ_PASSWORD must be changed from the default 'guest' when DEBUG "
        "is off. Set RABBITMQ_PASSWORD or include the password in RABBITMQ_URL."
    )
