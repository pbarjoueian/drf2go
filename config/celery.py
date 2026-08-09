"""
Celery application.

Imported by ``config/__init__.py`` so that ``@shared_task`` always binds to this
app, whichever entrypoint (Django, worker, beat) started the process.
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("drf2go")

# All CELERY_-prefixed Django settings become Celery configuration; see
# config/settings/sub_settings/celery_conf.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Discover tasks.py in every installed app.
app.autodiscover_tasks()

# Static schedule entries. django-celery-beat's DatabaseScheduler syncs these
# into the database on startup, after which they can be edited from the admin.
app.conf.beat_schedule = {
    "simple-periodic-task": {
        "task": "core.tasks.periodic_task",
        "schedule": crontab(minute="*/30"),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Log the request context; useful for confirming a worker is reachable."""
    import logging

    logging.getLogger("celery").info("debug_task request: %r", self.request)
