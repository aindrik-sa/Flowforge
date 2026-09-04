"""
Shared test fixtures for FlowForge.

WHAT: Centralized fixtures used across all test modules.
WHY:  DRY — every test file needs an API client and often a test user.
      Defining them here once means consistent test setup everywhere.
IMPORTANT: These fixtures use the database. pytest-django's @pytest.mark.django_db
           decorator is still required on test functions that use them.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """
    Factory fixture that creates a user with sensible defaults.
    Usage: user = create_user(email="test@example.com")
    """

    def _create_user(**kwargs):
        defaults = {
            "email": "testuser@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        defaults.update(kwargs)
        password = defaults.pop("password")
        user = User.objects.create_user(password=password, **defaults)
        return user

    return _create_user


@pytest.fixture
def user(create_user):
    """A single pre-created test user."""
    return create_user()


@pytest.fixture
def authenticated_client(api_client, user) -> APIClient:
    """
    API client with JWT authentication already set up.
    The user fixture is automatically created and authenticated.
    """
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
    )
    return api_client
