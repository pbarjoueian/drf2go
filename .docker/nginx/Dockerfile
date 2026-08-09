# Nginx reverse proxy in front of the Daphne ASGI server.
#
# Build context is the repository root:
#   docker build -f .docker/nginx/Dockerfile .
FROM nginx:1.30-alpine

# `default.conf.template` is rendered by the official image's envsubst entrypoint,
# so SERVER_NAME / UPSTREAM_* can be set per environment without rebuilding.
COPY .docker/nginx/nginx.conf /etc/nginx/templates/default.conf.template

ENV SERVER_NAME=_ \
    UPSTREAM_HOST=web \
    UPSTREAM_PORT=8000 \
    CLIENT_MAX_BODY_SIZE=100M

# /app/static and /app/media are shared volumes: Django writes them, nginx only
# reads them. Docker seeds a fresh named volume with the ownership of whichever
# container mounts it first, so these directories must be owned by the *Django*
# user (uid 1001, see .docker/django/Dockerfile) - otherwise a boot order where
# nginx wins the race leaves collectstatic with a read-only directory. Mode 755
# still lets the unprivileged nginx worker read them.
ARG APP_UID=1001
ARG APP_GID=1001
RUN mkdir -p /app/static /app/media \
    && chown -R ${APP_UID}:${APP_GID} /app/static /app/media \
    && chmod 755 /app/static /app/media

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --spider -q http://127.0.0.1/healthz/ || exit 1
