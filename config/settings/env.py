"""
Environment loading.

`BASE_DIR` and `env` are the two things every settings module needs, so they
live here and nowhere else. Reading the ``.env`` file is anchored to the project
root rather than the current working directory, which keeps `manage.py`,
Celery workers and one-off `docker compose run` invocations consistent.

Real environment variables always win over values in ``.env`` (django-environ's
``read_env`` never overrides an existing key), so container orchestration can
override anything the file declares.
"""

from pathlib import Path

import environ

# config/settings/env.py -> config/settings -> config -> <project root>
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

ENV_FILE = Path(env("DJANGO_ENV_FILE", default=str(BASE_DIR / ".env")))
if ENV_FILE.is_file():
    env.read_env(str(ENV_FILE))
