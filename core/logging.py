"""
Structured logging utilities for the application.

This module provides helper functions and utilities for structured logging
that can be used throughout the application for consistent log formatting
and context enrichment.
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional


def get_logger(name: str = "app") -> logging.Logger:
    """
    Get a logger instance for the application.

    Args:
        name: Logger name (default: 'app').
            Use '__name__' for module-specific loggers.

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return logging.getLogger(name)


def log_request_response(
    logger: Optional[logging.Logger] = None,
    log_level: int = logging.INFO,
    include_request_body: bool = False,
    include_response_body: bool = False,
):
    """
    Decorator to log API request and response details.

    This decorator can be used with Django REST Framework views or
    function-based views to automatically log request/response information.

    Args:
        logger: Logger instance (default: uses 'app' logger)
        log_level: Logging level (default: INFO)
        include_request_body: Whether to log request body (default: False)
        include_response_body: Whether to log response body (default: False)

    Example:
        >>> @log_request_response(log_level=logging.DEBUG)
        >>> def my_api_view(request):
        >>>     return Response({"status": "ok"})
    """
    if logger is None:
        logger = get_logger("app")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract request from args or kwargs
            request = None
            if args and hasattr(args[0], "request"):
                request = args[0].request
            elif "request" in kwargs:
                request = kwargs["request"]
            elif args and hasattr(args[0], "META"):
                request = args[0]

            if request:
                log_data = {
                    "method": request.method,
                    "path": request.path,
                    "user": getattr(request, "user", None),
                    "remote_addr": request.META.get("REMOTE_ADDR"),
                    "user_agent": request.META.get("HTTP_USER_AGENT"),
                }

                if include_request_body and hasattr(request, "body"):
                    try:
                        log_data["request_body"] = request.body.decode("utf-8")
                    except Exception:
                        log_data["request_body"] = "<unable to decode>"

                logger.log(
                    log_level,
                    f"Request: {request.method} {request.path}",
                    extra=log_data,
                )

            # Execute the function
            response = func(*args, **kwargs)

            # Log response if it's a DRF Response
            if request and hasattr(response, "status_code"):
                response_data = {
                    "status_code": response.status_code,
                    "method": request.method,
                    "path": request.path,
                }

                if include_response_body and hasattr(response, "data"):
                    # Limit size
                    response_data["response_body"] = str(response.data)[:500]

                msg = (
                    f"Response: {request.method} {request.path} "
                    f"- {response.status_code}"
                )
                logger.log(log_level, msg, extra=response_data)

            return response

        return wrapper

    return decorator


def log_execution_time(
    logger: Optional[logging.Logger] = None,
    log_level: int = logging.INFO,
    log_slow_queries: bool = True,
    slow_query_threshold: float = 1.0,
):
    """
    Decorator to log function execution time.

    Args:
        logger: Logger instance (default: uses 'app' logger)
        log_level: Logging level (default: INFO)
        log_slow_queries: Whether to log slow queries at WARNING level
        slow_query_threshold: Threshold in seconds for slow query warning

    Example:
        >>> @log_execution_time()
        >>> def expensive_operation():
        >>>     # ... operation code ...
        >>>     pass
    """
    if logger is None:
        logger = get_logger("app")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                log_data = {
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "module": func.__module__,
                }

                if execution_time > slow_query_threshold and log_slow_queries:
                    msg = (
                        f"Slow execution: {func.__name__} "
                        f"took {execution_time:.2f}s"
                    )
                    logger.warning(msg, extra=log_data)
                else:
                    msg = (
                        f"Execution: {func.__name__} completed "
                        f"in {execution_time:.2f}s"
                    )
                    logger.log(log_level, msg, extra=log_data)

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                msg = (
                    f"Execution failed: {func.__name__} "
                    f"after {execution_time:.2f}s - {str(e)}"
                )
                logger.error(
                    msg,
                    extra={
                        "function": func.__name__,
                        "execution_time": execution_time,
                        "error": str(e),
                        "module": func.__module__,
                    },
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def log_exception(
    logger: Optional[logging.Logger] = None,
    log_level: int = logging.ERROR,
    include_traceback: bool = True,
):
    """
    Context manager to log exceptions with context.

    Args:
        logger: Logger instance (default: uses 'app' logger)
        log_level: Logging level (default: ERROR)
        include_traceback: Whether to include full traceback (default: True)

    Example:
        >>> with log_exception():
        >>>     # code that might raise an exception
        >>>     risky_operation()
    """
    if logger is None:
        logger = get_logger("app")

    class ExceptionLogger:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            if exc_type is not None:
                msg = f"Exception occurred: {exc_type.__name__}: " f"{exc_value}"
                if include_traceback:
                    logger.log(
                        log_level,
                        msg,
                        exc_info=(exc_type, exc_value, exc_traceback),
                    )
                else:
                    logger.log(log_level, msg)
                # Don't suppress the exception
                return False

    return ExceptionLogger()


def enrich_log_context(**context: Any) -> Dict[str, Any]:
    """
    Create a dictionary of context data for structured logging.

    Args:
        **context: Key-value pairs to include in log context

    Returns:
        dict: Context dictionary for use with logger's 'extra' parameter

    Example:
        >>> logger.info(
        >>>     "User action",
        >>>     extra=enrich_log_context(user_id=123, action="login")
        >>> )
    """
    return context
