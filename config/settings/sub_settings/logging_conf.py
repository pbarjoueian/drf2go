"""
Logging configuration.

Supports console logging (the default, and what container platforms want),
optional rotating file logging, and structured JSON output. Everything is driven
by environment variables:

    LOG_LEVEL              DEBUG | INFO | WARNING | ERROR | CRITICAL
    LOG_ALL_LEVELS         force DEBUG everywhere, overriding LOG_LEVEL
    LOG_TO_CONSOLE         stream to stdout                      (default: True)
    LOG_TO_FILE            write rotating files under LOG_DIR    (default: False)
    LOG_FORMAT             verbose | json                        (default: verbose)
    LOG_DIR                directory for log files
    LOG_FILE_MAX_BYTES     rotate after this many bytes
    LOG_FILE_BACKUP_COUNT  how many rotated files to keep
    LOG_DB_QUERIES         log every SQL statement               (default: False)
"""

from pathlib import Path

from ..env import BASE_DIR, env

LOG_LEVEL = env("LOG_LEVEL", default="INFO").upper()
LOG_ALL_LEVELS = env.bool("LOG_ALL_LEVELS", default=False)
LOG_TO_CONSOLE = env.bool("LOG_TO_CONSOLE", default=True)
LOG_TO_FILE = env.bool("LOG_TO_FILE", default=False)
LOG_FORMAT = env("LOG_FORMAT", default="verbose").lower()
LOG_DIR = Path(env("LOG_DIR", default=str(BASE_DIR / "logs")))
LOG_FILE_MAX_BYTES = env.int("LOG_FILE_MAX_BYTES", default=10 * 1024 * 1024)
LOG_FILE_BACKUP_COUNT = env.int("LOG_FILE_BACKUP_COUNT", default=5)
LOG_DB_QUERIES = env.bool("LOG_DB_QUERIES", default=False)

if LOG_ALL_LEVELS:
    LOG_LEVEL = "DEBUG"

if LOG_FORMAT not in {"verbose", "json"}:
    LOG_FORMAT = "verbose"

if LOG_TO_FILE:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _formatters() -> dict:
    return {
        "verbose": {
            "format": (
                "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d "
                "%(funcName)s() - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": (
                "%(asctime)s %(name)s %(levelname)s %(pathname)s "
                "%(lineno)d %(funcName)s %(message)s"
            ),
        },
    }


def _file_handler(filename: str, level: str | None = None) -> dict:
    return {
        "class": "logging.handlers.RotatingFileHandler",
        "level": level or LOG_LEVEL,
        "formatter": LOG_FORMAT,
        "filename": str(LOG_DIR / filename),
        "maxBytes": LOG_FILE_MAX_BYTES,
        "backupCount": LOG_FILE_BACKUP_COUNT,
        "encoding": "utf-8",
    }


def _build_logging_config() -> dict:
    handlers: dict = {}

    if LOG_TO_CONSOLE or not LOG_TO_FILE:
        # Console is the fallback so a misconfiguration never silences logging.
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": LOG_FORMAT,
            "stream": "ext://sys.stdout",
        }

    if LOG_TO_FILE:
        handlers["file"] = _file_handler("application.log")
        handlers["error_file"] = _file_handler(
            "error.log", level="DEBUG" if LOG_ALL_LEVELS else "ERROR"
        )
        handlers["db_file"] = _file_handler("database.log", level="DEBUG")

    default_handlers = [name for name in handlers if name != "db_file"]
    db_handlers = ["db_file"] if LOG_TO_FILE else default_handlers

    def logger(level: str, names: list[str] | None = None) -> dict:
        return {
            "handlers": names or default_handlers,
            "level": "DEBUG" if LOG_ALL_LEVELS else level,
            "propagate": False,
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": _formatters(),
        "handlers": handlers,
        "root": logger(LOG_LEVEL),
        "loggers": {
            "django": logger("INFO"),
            "django.request": logger("WARNING"),
            "django.server": logger("INFO"),
            "django.template": logger("INFO"),
            "django.security": logger("WARNING"),
            "django.db.backends": logger(
                "DEBUG" if LOG_DB_QUERIES else "INFO", db_handlers
            ),
            "django.channels.server": logger("INFO"),
            "celery": logger("INFO"),
            "rest_framework": logger("INFO"),
            "drf_spectacular": logger("INFO"),
            # Namespace for application code: core.logging.get_logger(__name__).
            "app": logger(LOG_LEVEL),
            "core": logger(LOG_LEVEL),
        },
    }


LOGGING = _build_logging_config()
