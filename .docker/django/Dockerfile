# syntax=docker/dockerfile:1.7
#
# Django image for drf2go.
#
# Build context is the repository root; build from the repo root with:
#   docker build -f .docker/django/Dockerfile --target development .
#   docker build -f .docker/django/Dockerfile --target production  .
#
# Dependencies come exclusively from Pipfile / Pipfile.lock. `pipenv requirements`
# renders the lock (including hashes) so pip installs a byte-for-byte reproducible
# dependency set into a self-contained virtualenv at /opt/venv. The venv lives
# outside /app on purpose: the development stack bind-mounts the source tree over
# /app and would otherwise shadow it.

ARG PYTHON_VERSION=3.13
ARG PIPENV_VERSION=2026.7.1

# ---------------------------------------------------------------------------
# base - shared runtime foundation
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# curl is used by container healthchecks; tini gives us correct PID 1 signal
# handling so `docker compose stop` terminates Daphne/Celery gracefully.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends curl tini \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]

# ---------------------------------------------------------------------------
# lockfile - renders Pipfile.lock into a hash-pinned requirements set
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS lockfile
ARG PIPENV_VERSION

RUN pip install --no-cache-dir "pipenv==${PIPENV_VERSION}"

WORKDIR /src
COPY Pipfile Pipfile.lock ./

# --deploy fails the build if Pipfile and Pipfile.lock have drifted apart.
RUN pipenv verify \
    && pipenv requirements > /tmp/requirements.txt \
    && pipenv requirements --dev > /tmp/requirements-dev.txt

# ---------------------------------------------------------------------------
# venv-prod / venv-dev - isolated dependency builds
# ---------------------------------------------------------------------------
FROM base AS venv-prod
RUN --mount=type=bind,from=lockfile,source=/tmp/requirements.txt,target=/tmp/requirements.txt \
    python -m venv "$VIRTUAL_ENV" \
    && pip install --no-cache-dir -r /tmp/requirements.txt

FROM base AS venv-dev
RUN --mount=type=bind,from=lockfile,source=/tmp/requirements-dev.txt,target=/tmp/requirements.txt \
    python -m venv "$VIRTUAL_ENV" \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# ---------------------------------------------------------------------------
# development - source is bind-mounted, runs as root for painless file access
# ---------------------------------------------------------------------------
FROM base AS development

ENV DJANGO_SETTINGS_MODULE=config.settings \
    DJANGO_ENV=development

COPY --from=venv-dev /opt/venv /opt/venv
COPY .docker/django/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# The compose file bind-mounts the working tree over /app; this COPY only makes
# the image usable standalone (e.g. `docker run` for a one-off management command).
COPY . /app
RUN mkdir -p /app/logs /app/static /app/media

EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]

# ---------------------------------------------------------------------------
# production - immutable image, unprivileged user, no dev dependencies
# ---------------------------------------------------------------------------
FROM base AS production

ENV DJANGO_SETTINGS_MODULE=config.settings \
    DJANGO_ENV=production

COPY --from=venv-prod /opt/venv /opt/venv
COPY .docker/django/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home --home-dir /home/app app

COPY --chown=app:app . /app
RUN mkdir -p /app/logs /app/static /app/media \
    && chown -R app:app /app/logs /app/static /app/media

USER app

EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
