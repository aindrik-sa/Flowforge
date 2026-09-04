"""
Tests for authentication API endpoints.

Covers:
- POST /api/v1/auth/register/   — user registration
- POST /api/v1/auth/login/      — user login
- POST /api/v1/auth/refresh/    — token refresh
- GET  /api/v1/auth/me/         — current user profile

Tests both success and failure cases including:
- Valid registration
- Duplicate email
- Weak password
- Invalid login credentials
- Token refresh
- Authenticated vs unauthenticated access
"""
import pytest
from django.urls import reverse
from rest_framework import status

REGISTER_URL = reverse("accounts:register")
LOGIN_URL = reverse("accounts:login")
REFRESH_URL = reverse("accounts:token-refresh")
ME_URL = reverse("accounts:me")


@pytest.mark.django_db
class TestRegisterAPI:
    """Tests for POST /api/v1/auth/register/"""

    def test_register_success(self, api_client):
        """Valid registration should return 201 with user data."""
        payload = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "first_name": "Jane",
            "last_name": "Doe",
        }
        response = api_client.post(REGISTER_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "newuser@example.com"
        assert response.data["first_name"] == "Jane"
        assert "password" not in response.data  # password must not leak
        assert "id" in response.data

    def test_register_without_optional_fields(self, api_client):
        """Registration should work with only email and password."""
        payload = {
            "email": "minimal@example.com",
            "password": "strongpass123",
        }
        response = api_client.post(REGISTER_URL, payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_duplicate_email(self, api_client, create_user):
        """Registering with an existing email should return 400."""
        create_user(email="taken@example.com")

        payload = {
            "email": "taken@example.com",
            "password": "strongpass123",
        }
        response = api_client.post(REGISTER_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client):
        """Password shorter than 8 characters should be rejected."""
        payload = {
            "email": "short@example.com",
            "password": "abc",
        }
        response = api_client.post(REGISTER_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_email(self, api_client):
        """Registration without email should return 400."""
        payload = {"password": "strongpass123"}
        response = api_client.post(REGISTER_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_password(self, api_client):
        """Registration without password should return 400."""
        payload = {"email": "nopw@example.com"}
        response = api_client.post(REGISTER_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, api_client):
        """Registration with invalid email format should return 400."""
        payload = {
            "email": "not-an-email",
            "password": "strongpass123",
        }
        response = api_client.post(REGISTER_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    """Tests for POST /api/v1/auth/login/"""

    def test_login_success(self, api_client, create_user):
        """Valid credentials should return 200 with user data and tokens."""
        create_user(email="login@example.com", password="testpass123")

        payload = {
            "email": "login@example.com",
            "password": "testpass123",
        }
        response = api_client.post(LOGIN_URL, payload)

        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert "user" in response.data
        assert response.data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self, api_client, create_user):
        """Wrong password should return 400."""
        create_user(email="wrong@example.com", password="correctpass")

        payload = {
            "email": "wrong@example.com",
            "password": "wrongpass",
        }
        response = api_client.post(LOGIN_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self, api_client):
        """Login with non-existent email should return 400."""
        payload = {
            "email": "ghost@example.com",
            "password": "testpass123",
        }
        response = api_client.post(LOGIN_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_inactive_user(self, api_client, create_user):
        """Inactive user should not be able to log in."""
        user = create_user(email="inactive@example.com", password="testpass123")
        user.is_active = False
        user.save()

        payload = {
            "email": "inactive@example.com",
            "password": "testpass123",
        }
        response = api_client.post(LOGIN_URL, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefreshAPI:
    """Tests for POST /api/v1/auth/refresh/"""

    def test_refresh_token_success(self, api_client, create_user):
        """Valid refresh token should return a new access token."""
        create_user(email="refresh@example.com", password="testpass123")

        # First, login to get tokens
        login_response = api_client.post(
            LOGIN_URL,
            {"email": "refresh@example.com", "password": "testpass123"},
        )
        refresh_token = login_response.data["tokens"]["refresh"]

        # Then, use refresh token
        response = api_client.post(REFRESH_URL, {"refresh": refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_refresh_with_invalid_token(self, api_client):
        """Invalid refresh token should return 401."""
        response = api_client.post(REFRESH_URL, {"refresh": "invalid-token"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMeAPI:
    """Tests for GET /api/v1/auth/me/"""

    def test_me_authenticated(self, authenticated_client, user):
        """Authenticated user should get their profile data."""
        response = authenticated_client.get(ME_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
        assert response.data["id"] == str(user.id)
        assert "password" not in response.data

    def test_me_unauthenticated(self, api_client):
        """Unauthenticated request to /me should return 401."""
        response = api_client.get(ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
