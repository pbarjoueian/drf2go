"""
Logging configuration for Django application.

This module provides comprehensive logging configuration that supports:
- Console logging (for development and Docker environments)
- File logging (for production environments)
- Structured logging with JSON format option
- Log rotation and retention policies
- Separate handlers for different log levels
- Environment-based configuration
"""

from pathlib import Path

from ..env import env

# Get base directory for log file paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Logging configuration from environment variables
LOG_LEVEL = env("LOG_LEVEL", default="INFO").upper()
LOG_ALL_LEVELS = env.bool("LOG_ALL_LEVELS", default=False)
LOG_TO_CONSOLE = env.bool("LOG_TO_CONSOLE", default=True)
LOG_TO_FILE = env.bool("LOG_TO_FILE", default=False)
LOG_FORMAT = env("LOG_FORMAT", default="verbose")  # 'verbose' or 'json'
LOG_DIR = env("LOG_DIR", default=str(BASE_DIR / "logs"))
# 10MB default
LOG_FILE_MAX_BYTES = env.int("LOG_FILE_MAX_BYTES", default=10 * 1024 * 1024)
LOG_FILE_BACKUP_COUNT = env.int("LOG_FILE_BACKUP_COUNT", default=5)
LOG_FILE_RETENTION_DAYS = env.int("LOG_FILE_RETENTION_DAYS", default=30)

# If LOG_ALL_LEVELS is enabled, force DEBUG level to capture everything
if LOG_ALL_LEVELS:
    LOG_LEVEL = "DEBUG"

# Ensure log directory exists
log_path = Path(LOG_DIR)
log_path.mkdir(parents=True, exist_ok=True)


def get_log_formatters():
    """Get log formatters based on configuration."""
    global LOG_FORMAT

    formatters = {
        "verbose": {
            "format": (
                "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d "
                "%(funcName)s() - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
    }

    # Add JSON formatter if requested and available
    if LOG_FORMAT == "json":
        try:
            # Try to import pythonjsonlogger
            import pythonjsonlogger.jsonlogger  # noqa: F401

            formatters["json"] = {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": (
                    "%(asctime)s %(name)s %(levelname)s %(pathname)s "
                    "%(lineno)d %(funcName)s %(message)s"
                ),
            }
        except ImportError:
            # Fall back to verbose format if pythonjsonlogger is not installed
            import warnings

            msg = (
                "pythonjsonlogger not installed. "
                "Falling back to 'verbose' format. "
                "Install it with: pip install pythonjsonlogger"
            )
            warnings.warn(msg, UserWarning)
            # Update LOG_FORMAT to verbose for this session
            LOG_FORMAT = "verbose"

    return formatters


def get_console_handler():
    """Get console handler configuration."""
    # If LOG_ALL_LEVELS is enabled, use DEBUG to capture all levels
    level = LOG_LEVEL if not LOG_ALL_LEVELS else "DEBUG"
    handler = {
        "class": "logging.StreamHandler",
        "level": level,
        "formatter": LOG_FORMAT if LOG_FORMAT != "json" else "verbose",
        "stream": "ext://sys.stdout",
    }
    return handler


def get_file_handler(log_file_name, formatter_name=None, handler_level=None):
    """
    Get rotating file handler configuration.

    Args:
        log_file_name: Name of the log file
        formatter_name: Formatter to use (defaults to LOG_FORMAT)
        handler_level: Specific level for this handler
            (defaults to LOG_LEVEL or DEBUG if LOG_ALL_LEVELS)
    """
    if formatter_name is None:
        formatter_name = LOG_FORMAT if LOG_FORMAT != "json" else "verbose"

    # If LOG_ALL_LEVELS is enabled, use DEBUG to capture all levels
    level = handler_level or (LOG_LEVEL if not LOG_ALL_LEVELS else "DEBUG")

    handler = {
        "class": "logging.handlers.RotatingFileHandler",
        "level": level,
        "formatter": formatter_name,
        "filename": str(log_path / log_file_name),
        "maxBytes": LOG_FILE_MAX_BYTES,
        "backupCount": LOG_FILE_BACKUP_COUNT,
        "encoding": "utf-8",
    }
    return handler


def get_logging_config():
    """
    Build comprehensive logging configuration dictionary.

    Returns:
        dict: Django LOGGING configuration
    """
    formatters = get_log_formatters()

    handlers = {}
    handler_list = []

    # Console handler (always available, but can be disabled)
    if LOG_TO_CONSOLE:
        handlers["console"] = get_console_handler()
        handler_list.append("console")

    # File handlers (only if LOG_TO_FILE is enabled)
    if LOG_TO_FILE:
        # General application log (captures all levels if LOG_ALL_LEVELS)
        handlers["file"] = get_file_handler("application.log")
        handler_list.append("file")

        # Error log (separate file for errors and above)
        # If LOG_ALL_LEVELS, also capture all levels in error.log
        error_level = "DEBUG" if LOG_ALL_LEVELS else "ERROR"
        handlers["error_file"] = get_file_handler(
            "error.log", formatter_name="verbose", handler_level=error_level
        )
        handler_list.append("error_file")

        # Django-specific log
        handlers["django_file"] = get_file_handler("django.log")
        handler_list.append("django_file")

        # Database query log (for debugging)
        handlers["db_file"] = get_file_handler("database.log", handler_level="DEBUG")
        handler_list.append("db_file")

    # If no handlers are configured, use console as fallback
    if not handler_list:
        handlers["console"] = get_console_handler()
        handler_list = ["console"]

    # Determine logger level based on LOG_ALL_LEVELS setting
    # If LOG_ALL_LEVELS is enabled, all loggers use DEBUG to capture everything
    default_logger_level = "DEBUG" if LOG_ALL_LEVELS else LOG_LEVEL
    django_logger_level = "DEBUG" if LOG_ALL_LEVELS else "INFO"
    django_request_level = "DEBUG" if LOG_ALL_LEVELS else "WARNING"
    django_security_level = "DEBUG" if LOG_ALL_LEVELS else "WARNING"
    db_logger_level = (
        "DEBUG"
        if LOG_ALL_LEVELS or env.bool("LOG_DB_QUERIES", default=False)
        else "INFO"
    )

    # Logger configurations
    loggers = {
        # Root logger
        "": {
            "handlers": handler_list,
            "level": default_logger_level,
            "propagate": False,
        },
        # Django framework loggers
        "django": {
            "handlers": handler_list,
            "level": django_logger_level,
            "propagate": False,
        },
        "django.request": {
            "handlers": handler_list,
            "level": django_request_level,
            "propagate": False,
        },
        "django.server": {
            "handlers": handler_list,
            "level": django_logger_level,
            "propagate": False,
        },
        "django.template": {
            "handlers": handler_list,
            "level": django_logger_level,
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["db_file"] if LOG_TO_FILE else handler_list,
            "level": db_logger_level,
            "propagate": False,
        },
        # Security logger
        "django.security": {
            "handlers": handler_list,
            "level": django_security_level,
            "propagate": False,
        },
        # Third-party loggers
        "rest_framework": {
            "handlers": handler_list,
            "level": django_logger_level,
            "propagate": False,
        },
        "drf_spectacular": {
            "handlers": handler_list,
            "level": django_logger_level,
            "propagate": False,
        },
        # Application logger (for custom application code)
        "app": {
            "handlers": handler_list,
            "level": default_logger_level,
            "propagate": False,
        },
    }

    # If file logging is enabled, ensure error_file is in error loggers
    if LOG_TO_FILE and "error_file" in handlers:
        # Add error_file to loggers that should log errors separately
        for logger_name in ["django.request", "django.security"]:
            if logger_name in loggers:
                current_handlers = loggers[logger_name]["handlers"]
                if "error_file" not in current_handlers:
                    current_handlers.append("error_file")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers,
    }


# Set Django LOGGING configuration
LOGGING = get_logging_config()
