"""
Simple Celery tasks for demonstration.

This module contains basic async and periodic task examples.
"""

from celery import shared_task


@shared_task
def simple_async_task(message: str) -> str:
    """
    Simple async task example.

    Args:
        message: A message to process

    Returns:
        str: Processed message
    """
    return f"Processed: {message}"


@shared_task
def periodic_task() -> str:
    """
    Simple periodic task example.

    This task can be scheduled to run periodically.

    Returns:
        str: Task result
    """
    return "Periodic task executed"
