"""
Test settings for FlowForge.

Optimized for fast test execution.
"""
from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = False

# ---------------------------------------------------------------------------
# Password hashing — use fast hasher for tests
# ---------------------------------------------------------------------------
# WHAT: MD5PasswordHasher is ~10x faster than PBKDF2 (the production default).
# WHY:  Tests create many users. Slow hashing adds up to minutes of wasted time.
# IMPORTANT: This is test-only. Production uses PBKDF2 (Django's default).
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ---------------------------------------------------------------------------
# Email — capture emails in memory instead of sending
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ---------------------------------------------------------------------------
# Database — use SQLite for tests (no Docker dependency)
# ---------------------------------------------------------------------------
# WHAT: Override PostgreSQL with SQLite for test runs.
# WHY:  Tests should run fast and without external services.
#       SQLite is sufficient for unit and API tests.
# IMPORTANT: Integration tests that rely on PostgreSQL-specific features
#            (full-text search, JSON operators) should run against PostgreSQL
#            in CI. For now, SQLite covers all Sprint 1 tests.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_STORE_EAGER_RESULT = True

# ---------------------------------------------------------------------------
# Django Channels
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# ---------------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
