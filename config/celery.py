"""
Celery configuration for Django project.

This module configures Celery to work with Django and RabbitMQ as the message broker.
"""

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("drf_r2go")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Explicitly import tasks from core app
app.autodiscover_tasks(["core"])

# Periodic task schedule
# Define periodic tasks here - much simpler than management commands!
# These tasks run automatically when Celery beat starts
app.conf.beat_schedule = {
    "simple-periodic-task": {
        "task": "core.tasks.periodic_task",
        # Run every 30 minutes
        "schedule": crontab(minute="*/30"),
        # Alternative schedules:
        # "schedule": 1800.0,  # Every 30 minutes (in seconds)
        # "schedule": crontab(hour=0, minute=0),  # Daily at midnight
        # "schedule": crontab(hour="*/2"),  # Every 2 hours
    },
}

# Optional: Set timezone for periodic tasks
app.conf.timezone = "UTC"


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery setup."""
    print(f"Request: {self.request!r}")
