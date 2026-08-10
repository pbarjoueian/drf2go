"""
Base Django settings for the drf2go project.

Layout
------
``config.settings`` is the only settings module anything should import or point
``DJANGO_SETTINGS_MODULE`` at. It re-exports this module, which in turn pulls in
the focused modules under ``config/settings/sub_settings/`` (DRF, Celery,
RabbitMQ, Redis, Channels, CORS, logging, OpenAPI).

Everything environment-specific comes from environment variables, so the same
image runs in development and production - see ``.env.example``.

https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from django.core.exceptions import ImproperlyConfigured

from .env import BASE_DIR, env

# No __all__ here on purpose: `config/settings/__init__.py` does
# `from .base import *`, and defining __all__ would hide every setting that is
# not listed in it.

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

# "development" | "production" - a coarse switch for environment-specific
# defaults. Every individual setting stays overridable on its own.
DJANGO_ENV = env("DJANGO_ENV", default="development")
IS_PRODUCTION = DJANGO_ENV == "production"

DEBUG = env.bool("DEBUG", default=not IS_PRODUCTION)

# A missing SECRET_KEY is fatal outside development rather than silently
# falling back to a key that is committed to version control.
# A sentinel used to detect an unset key - not a credential.
_INSECURE_SECRET_KEY = "django-insecure-development-only-do-not-use-in-production"
SECRET_KEY = env("SECRET_KEY", default=_INSECURE_SECRET_KEY)
if not DEBUG and SECRET_KEY == _INSECURE_SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY must be set to a unique secret value when DEBUG is off. "
        "Generate one with: python -c 'from django.core.management.utils "
        "import get_random_secret_key; print(get_random_secret_key())'"
    )

# Comma-separated, e.g. ALLOWED_HOSTS=example.com,www.example.com
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Required by Django when POSTing to admin/API over HTTPS from a known origin.
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Path to the real admin. `/admin/` is served by the honeypot, so moving this
# to a non-guessable value is the point of installing admin_honeypot at all.
ADMIN_URL = env("ADMIN_URL", default="secret-admin/").lstrip("/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

DJANGO_APPS = [
    "daphne",  # must precede staticfiles so runserver speaks ASGI
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    # Required for SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] to actually revoke
    # rotated refresh tokens rather than silently doing nothing.
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    # Loaded through an AppConfig override so DEFAULT_AUTO_FIELD does not create
    # permanent migration drift against its vendored schema.
    "config.app_configs.AdminHoneypotConfig",
    "corsheaders",
    "django_celery_beat",
    "channels",
]

# Project apps all live under `apps/` and are named `apps.<name>`. `apps.core`
# is installed so its management commands, Celery tasks and Channels consumers
# are discovered.
LOCAL_APPS = [
    "apps.core",
]

INSTALLED_APPS = [*DJANGO_APPS, *THIRD_PARTY_APPS, *LOCAL_APPS]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

# Three ways to point at a database, in order of precedence:
#
#   1. DATABASE_URL          - a full URL; use this for managed/external databases
#   2. POSTGRES_*            - discrete parameters; what the compose stacks set
#   3. nothing               - SQLite, so a fresh checkout runs without services
#
# Discrete parameters are the default because a password containing "@", ":",
# "/" or "%" cannot be embedded in a URL without escaping, and silently
# mis-parsing a connection string is a miserable failure mode.

DATABASE_URL = env("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {"default": env.db_url_config(DATABASE_URL)}
elif env("POSTGRES_DB", default=""):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER", default="postgres"),
            "PASSWORD": env("POSTGRES_PASSWORD", default=""),
            "HOST": env("POSTGRES_HOST", default="db"),
            "PORT": env.int("POSTGRES_PORT", default=5432),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Persistent connections plus liveness checks: the single biggest throughput win
# for a containerised Django app, and safe because psycopg3 revalidates a
# connection before handing it back out.
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"].update(
        CONN_MAX_AGE=env.int("DB_CONN_MAX_AGE", default=60),
        CONN_HEALTH_CHECKS=True,
    )

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
# Only tightened when DEBUG is off so local HTTP development is unaffected.
# SECURE_SSL_REDIRECT stays opt-in: the bundled nginx terminates plain HTTP, so
# enabling it before TLS is configured would produce a redirect loop.

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
    )
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
    X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Feature-specific settings
# ---------------------------------------------------------------------------

from .sub_settings import *
