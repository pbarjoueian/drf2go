#!/bin/sh
# Unified entrypoint for both development and production containers
set -e

# Wait for PostgreSQL to be ready
wait_for_postgres() {
  # Use POSTGRES_* env vars if available (docker-compose), otherwise parse DATABASE_URL
  if [ -n "${POSTGRES_DB}" ] && [ -n "${POSTGRES_USER}" ]; then
    DB_HOST="${POSTGRES_HOST:-db}"
    DB_NAME="${POSTGRES_DB}"
    DB_USER="${POSTGRES_USER}"
    DB_PASS="${POSTGRES_PASSWORD}"
  elif echo "${DATABASE_URL}" | grep -q "postgresql://"; then
    # Parse DATABASE_URL: postgresql://user:password@host:port/dbname
    DB_HOST=$(echo "${DATABASE_URL}" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    DB_NAME=$(echo "${DATABASE_URL}" | sed -n 's|.*/\([^?]*\).*|\1|p')
    DB_USER=$(echo "${DATABASE_URL}" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
    DB_PASS=$(echo "${DATABASE_URL}" | sed -n 's|postgresql://[^:]*:\([^@]*\)@.*|\1|p')
  else
    # Not using PostgreSQL, skip wait
    return 0
  fi

  if [ -n "${DB_HOST}" ] && [ -n "${DB_NAME}" ] && [ -n "${DB_USER}" ]; then
    echo "Waiting for PostgreSQL to be ready..."
    until python -c "import psycopg2; psycopg2.connect(host='${DB_HOST}', dbname='${DB_NAME}', user='${DB_USER}', password='${DB_PASS}')" 2>/dev/null; do
      echo "PostgreSQL is unavailable - sleeping"
      sleep 1
    done
    echo "PostgreSQL is up"
  fi
}

# Wait for database if using PostgreSQL
wait_for_postgres || echo "Database wait skipped or not using PostgreSQL"

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --noinput || echo "Migration failed or not configured"

# Determine if we're in production or development mode
# Production: no command passed or command starts with "uwsgi"
# Development: any other command (typically "python manage.py runserver")
IS_PRODUCTION=false
if [ $# -eq 0 ]; then
  IS_PRODUCTION=true
elif [ "$1" = "uwsgi" ]; then
  IS_PRODUCTION=true
fi

if [ "$IS_PRODUCTION" = "true" ]; then
  # Production mode
  echo "Running in production mode"
  echo "Collecting static files"
  python manage.py collectstatic --noinput || echo "collectstatic failed or not configured"
  
  # Start uWSGI if no command was provided
  if [ $# -eq 0 ]; then
    echo "Starting uWSGI"
    exec uwsgi --ini /app/uwsgi.ini
  else
    # Execute the provided command (likely uwsgi)
    exec "$@"
  fi
else
  # Development mode - execute the passed command
  echo "Running in development mode"
  exec "$@"
fi
