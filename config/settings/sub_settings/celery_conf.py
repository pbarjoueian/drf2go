"""
Celery configuration settings.

This module contains all Celery-related settings for the Django project.
"""

from ..env import env

# Import RabbitMQ configuration
# RABBITMQ_URL is built from individual parameters or parsed from RABBITMQ_URL env var
from .rabbitmq_conf import RABBITMQ_URL  # noqa

# Celery Configuration
# https://docs.celeryproject.org/en/stable/userguide/configuration.html

# Use RabbitMQ URL from rabbitmq_conf.py
# CELERY_BROKER_URL can still be overridden via environment variable for flexibility
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL",
    default=RABBITMQ_URL,
)
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND",
    default="rpc://",
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = env("TIME_ZONE", default="UTC")
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 60  # 1 minute
# Use DatabaseScheduler to allow dynamic task management via Django admin
# Static tasks can be defined in config/celery.py using beat_schedule
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
