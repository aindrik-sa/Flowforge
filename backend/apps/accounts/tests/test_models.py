"""
Tests for the User model and CustomUserManager.

Covers:
- User creation with email
- Superuser creation
- Email normalization
- Missing email validation
- Superuser flag validation
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Tests for the custom User model."""

    def test_create_user_with_email(self):
        """User can be created with email as the primary identifier."""
        user = User.objects.create_user(
            email="test@example.com",
            password="securepass123",
            first_name="John",
            last_name="Doe",
        )
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("securepass123")

    def test_user_has_uuid_primary_key(self):
        """User ID should be a UUID, not an auto-incrementing integer."""
        user = User.objects.create_user(
            email="uuid@example.com", password="testpass123"
        )
        assert user.id is not None
        assert len(str(user.id)) == 36  # UUID format: 8-4-4-4-12

    def test_user_has_timestamps(self):
        """User should have created_at and updated_at from BaseModel."""
        user = User.objects.create_user(
            email="timestamps@example.com", password="testpass123"
        )
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_str_returns_email(self):
        """String representation of user should be their email."""
        user = User.objects.create_user(
            email="str@example.com", password="testpass123"
        )
        assert str(user) == "str@example.com"

    def test_email_is_normalized(self):
        """Email domain should be lowercased during creation."""
        user = User.objects.create_user(
            email="test@EXAMPLE.COM", password="testpass123"
        )
        assert user.email == "test@example.com"

    def test_create_user_without_email_raises_error(self):
        """Creating a user without email should raise ValueError."""
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="testpass123")

    def test_password_is_hashed(self):
        """Password should never be stored in plain text."""
        user = User.objects.create_user(
            email="hash@example.com", password="mypassword"
        )
        assert user.password != "mypassword"
        assert user.check_password("mypassword")

    def test_duplicate_email_raises_error(self):
        """Two users with the same email should not be allowed."""
        User.objects.create_user(
            email="dupe@example.com", password="testpass123"
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                email="dupe@example.com", password="testpass456"
            )


@pytest.mark.django_db
class TestSuperuserCreation:
    """Tests for superuser creation via CustomUserManager."""

    def test_create_superuser(self):
        """Superuser should have is_staff and is_superuser set to True."""
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_active is True

    def test_superuser_without_is_staff_raises_error(self):
        """Superuser with is_staff=False should raise ValueError."""
        with pytest.raises(ValueError, match="is_staff=True"):
            User.objects.create_superuser(
                email="bad@example.com",
                password="testpass123",
                is_staff=False,
            )

    def test_superuser_without_is_superuser_raises_error(self):
        """Superuser with is_superuser=False should raise ValueError."""
        with pytest.raises(ValueError, match="is_superuser=True"):
            User.objects.create_superuser(
                email="bad2@example.com",
                password="testpass123",
                is_superuser=False,
            )
