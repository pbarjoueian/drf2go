#!/usr/bin/env sh
#
# Shared entrypoint for every Django-based container (web, celery worker, beat).
#
# Behaviour is driven entirely by environment variables so the exact same image
# can be started as an API server, a worker or a scheduler:
#
#   WAIT_FOR_DB         wait until the configured database accepts connections (default: true)
#   AUTO_MIGRATE        run `manage.py migrate` before starting (default: false)
#   AUTO_COLLECTSTATIC  run `manage.py collectstatic` before starting (default: false)
#
# Migrations and collectstatic default to *off* so that scaling the stack to
# several web/worker replicas does not race several `migrate` runs against each
# other. Exactly one service in each compose file opts in.

set -eu

log() { printf '[entrypoint] %s\n' "$*" >&2; }

wait_for_db() {
    log "waiting for the database to accept connections..."
    python <<'PYTHON'
import sys
import time

import django

django.setup()

from django.db import connections
from django.db.utils import OperationalError

DEADLINE = time.monotonic() + 60
connection = connections["default"]

while True:
    try:
        connection.ensure_connection()
    except OperationalError as exc:
        if time.monotonic() >= DEADLINE:
            sys.exit(f"database did not become available in time: {exc}")
        time.sleep(1)
    else:
        connection.close()
        break
PYTHON
    log "database is ready"
}

if [ "${WAIT_FOR_DB:-true}" = "true" ]; then
    wait_for_db
fi

if [ "${AUTO_MIGRATE:-false}" = "true" ]; then
    log "applying database migrations"
    python manage.py migrate --noinput
fi

if [ "${AUTO_COLLECTSTATIC:-false}" = "true" ]; then
    log "collecting static files"
    python manage.py collectstatic --noinput --clear
fi

log "starting: $*"
exec "$@"
