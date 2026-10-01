"""
Production settings for FlowForge.

Security-focused settings for deployment.
"""
from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug — always False in production
# ---------------------------------------------------------------------------
DEBUG = False

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Allowed Hosts & CSRF
# ---------------------------------------------------------------------------
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="flowforge.example.com")
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="https://flowforge.example.com")

# ---------------------------------------------------------------------------
# Static Files & Media
# ---------------------------------------------------------------------------
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Email Backend
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.mailgun.org")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="FlowForge <noreply@flowforge.example.com>")