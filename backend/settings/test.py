from .base import *  # noqa: F403

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.PBKDF2PasswordHasher"]

REQUIRE_EMAIL_VERIFICATION = False
LOGGING["loggers"]["booktracker.requests"]["level"] = "WARNING"  # noqa: F405

AUTH_REDIS_URL = ""
