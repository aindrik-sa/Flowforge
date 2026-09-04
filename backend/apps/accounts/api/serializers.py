from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.services import create_user

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Handles user registration input validation.

    WHAT: Validates registration data and delegates creation to the service layer.
    WHY:  Serializers handle shape & validation. Services handle business logic.
          This separation means we can reuse `create_user()` from CLI, tests,
          or future invitation flows without duplicating validation.
    IMPORTANT: We use serializers.Serializer (not ModelSerializer) intentionally.
               ModelSerializer couples too tightly to the model and makes it
               tempting to put business logic in save().
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")

    def validate_email(self, value: str) -> str:
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def create(self, validated_data: dict) -> "User":
        return create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Authenticates user credentials and returns JWT tokens.

    WHAT: Takes email + password, returns access + refresh tokens.
    WHY:  Custom login (instead of simplejwt's TokenObtainPairView) gives us
          control over response shape, error messages, and future additions
          like login audit logging.
    IMPORTANT: We use Django's `authenticate()` which respects is_active.
               An inactive user will get "Invalid credentials" — not a hint
               about account status (security best practice).
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict) -> dict:
        email = attrs["email"].lower().strip()
        password = attrs["password"]

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": UserSerializer(user).data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for user profile data.
    Used by /me endpoint and nested in login response.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
