# ADR-002: Custom User Model

## Status
Accepted

## Context
Django's default `auth.User` uses a username field for authentication. FlowForge requires email-based authentication.

## Decision
Create a custom User model using `AbstractBaseUser` + `PermissionsMixin` with email as the unique identifier.

## Rationale
- **Email login**: Modern SaaS applications authenticate with email, not username.
- **Must be done first**: Django docs explicitly warn that changing the User model after migrations have been applied is extremely difficult.
- **Extensibility**: Custom model allows adding fields (avatar, phone, timezone) later.
- **Custom manager**: `CustomUserManager` handles email normalization and validation.

## Trade-offs
- More initial setup than using `AbstractUser`
- Must customize Django Admin for email-based fieldsets

## Key Implementation Details
- `USERNAME_FIELD = "email"`
- `REQUIRED_FIELDS = []` (email is already required by USERNAME_FIELD)
- `AUTH_USER_MODEL = "accounts.User"` in settings
- Custom `UserAdmin` with email-based ordering and fieldsets
