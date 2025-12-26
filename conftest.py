"""
Pytest configuration and shared fixtures for the project.
"""

import pytest


# Lazy imports - Django must be configured first
def get_user_model():
    """Lazy import of Django User model."""
    from django.contrib.auth import get_user_model as _get_user_model

    return _get_user_model()


def get_api_client():
    """Lazy import of DRF APIClient."""
    from rest_framework.test import APIClient

    return APIClient


@pytest.fixture
def api_client():
    """
    Fixture providing an unauthenticated API client.
    """
    APIClient = get_api_client()
    return APIClient()


@pytest.fixture
def authenticated_api_client(user):
    """
    Fixture providing an authenticated API client.

    Args:
        user: User instance created by the user fixture

    Returns:
        APIClient: Authenticated API client
    """
    APIClient = get_api_client()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user(db):
    """
    Fixture creating a test user.

    Args:
        db: Django database fixture

    Returns:
        User: Test user instance
    """
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpass123",
    )


@pytest.fixture
def superuser(db):
    """
    Fixture creating a test superuser.

    Args:
        db: Django database fixture

    Returns:
        User: Test superuser instance
    """
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )
