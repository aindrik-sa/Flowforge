from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


def create_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
) -> "User":
    """
    Create a new user account.

    WHAT: Service function that encapsulates user creation logic.
    WHY:  Keeps business rules (validation, normalization) in one place.
          Views stay thin. Serializers only handle input/output shape.
    IMPORTANT: Never call User.objects.create() directly in views —
               always go through this service so we have one place to
               add future logic (welcome email, default org, etc.).
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    return user
