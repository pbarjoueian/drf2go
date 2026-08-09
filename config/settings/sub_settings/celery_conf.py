"""
Celery configuration.

The broker defaults to the normalised RabbitMQ URL built in ``rabbitmq_conf``;
``CELERY_BROKER_URL`` overrides it when a broker outside this stack is used.
"""

from ..env import env
from .rabbitmq_conf import RABBITMQ_URL
from .redis_conf import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from .url_utils import build_url

# `or` rather than a default, so an explicitly empty value falls back too - the
# compose files export CELERY_BROKER_URL="" to mean "derive it from RABBITMQ_*".
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="") or RABBITMQ_URL

# Results go to Redis rather than the rpc:// backend: rpc:// creates one
# transient reply queue per client, which does not survive a restart and which
# RabbitMQ 4 only accepts as a deprecated feature. A dedicated Redis database
# keeps result keys out of the Channels layer's keyspace.
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="") or build_url(
    scheme="redis",
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    path=f"/{env.int('CELERY_RESULT_BACKEND_DB', default=1)}",
)
CELERY_RESULT_EXPIRES = env.int("CELERY_RESULT_EXPIRES", default=24 * 60 * 60)

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = env("TIME_ZONE", default="UTC")
CELERY_ENABLE_UTC = True

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = env.int("CELERY_TASK_TIME_LIMIT", default=30 * 60)
CELERY_TASK_SOFT_TIME_LIMIT = env.int("CELERY_TASK_SOFT_TIME_LIMIT", default=60)

# Fetch one message at a time and acknowledge after the task finishes: slightly
# slower, but tasks are not lost when a worker is killed mid-flight, which is
# what makes horizontal scaling of workers safe.
CELERY_WORKER_PREFETCH_MULTIPLIER = env.int(
    "CELERY_WORKER_PREFETCH_MULTIPLIER", default=1
)
CELERY_TASK_ACKS_LATE = env.bool("CELERY_TASK_ACKS_LATE", default=True)
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = env.int(
    "CELERY_WORKER_MAX_TASKS_PER_CHILD", default=1000
)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Schedules live in the database so they can be managed from the Django admin;
# entries declared in config/celery.py are synced into it on beat startup.
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
