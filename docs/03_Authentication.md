# FlowForge — Authentication

## Overview

FlowForge uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`.

- **Access token**: Short-lived (30 minutes), sent with every API request
- **Refresh token**: Long-lived (7 days), used to obtain new access tokens

## Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register/` | None | Create a new user account |
| POST | `/api/v1/auth/login/` | None | Authenticate and receive tokens |
| POST | `/api/v1/auth/refresh/` | None | Get a new access token |
| GET | `/api/v1/auth/me/` | JWT | Get current user profile |

## Registration

```
POST /api/v1/auth/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201):**
```json
{
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
}
```

## Login

```
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepass123"
}
```

**Response (200):**
```json
{
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "tokens": {
        "access": "eyJ...",
        "refresh": "eyJ..."
    }
}
```

## Token Refresh

```
POST /api/v1/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ..."
}
```

**Response (200):**
```json
{
    "access": "eyJ..."
}
```

## Using the Access Token

Include the token in the `Authorization` header:

```
GET /api/v1/auth/me/
Authorization: Bearer eyJ...
```

## Security Decisions

1. **Email-based login** — No username field. Email is the unique identifier.
2. **Password hashing** — Django's PBKDF2 hasher (default). Never stored in plain text.
3. **No password in responses** — `write_only=True` on all password fields.
4. **Inactive users blocked** — `authenticate()` respects `is_active`. Error message does not reveal account status.
5. **Minimum password length** — 8 characters enforced at the serializer level.

## Flow Diagram

```
Register → User created in DB
    ↓
Login → Credentials verified → JWT pair returned
    ↓
Access API → Bearer token in header → Request authenticated
    ↓
Token expired → Use refresh token → New access token
    ↓
Refresh expired → User must login again
```
