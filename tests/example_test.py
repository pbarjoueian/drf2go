"""
Example test file to demonstrate pytest configuration.
This file can be removed once you start writing actual tests.
"""

import pytest


@pytest.mark.django_db
def test_example():
    """
    Example test to verify pytest-django is working correctly.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    assert User.objects.count() == 0
    User.objects.create_user(
        username="example",
        email="example@example.com",
        password="password123",
    )
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_api_client_fixture(api_client):
    """
    Example test demonstrating the api_client fixture.
    """
    assert api_client is not None
    response = api_client.get("/admin/")
    # Admin endpoint should exist (may return 302 redirect or 403)
    assert response.status_code in [200, 302, 403]


@pytest.mark.django_db
def test_authenticated_api_client_fixture(authenticated_api_client, user):
    """
    Example test demonstrating the authenticated_api_client fixture.
    """
    assert authenticated_api_client is not None
    assert user is not None
    assert user.is_authenticated
