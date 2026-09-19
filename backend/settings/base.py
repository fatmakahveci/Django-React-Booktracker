"""Environment-based configuration; local development must be enabled explicitly."""

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parents[2]
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured(
        "Set DJANGO_SECRET_KEY to a unique random value of at least 50 characters."
    )


def env_list(name, default=""):
    return [value.strip() for value in os.environ.get(name, default).split(",") if value.strip()]


ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1" if DEBUG else "")
CORS_ALLOWED_ORIGINS = env_list(
    "DJANGO_CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173" if DEBUG else ""
)
CORS_EXPOSE_HEADERS = ["Retry-After"]
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.environ.get("DJANGO_HSTS_INCLUDE_SUBDOMAINS", "false").lower() == "true"
)
SECURE_HSTS_PRELOAD = os.environ.get("DJANGO_HSTS_PRELOAD", "false").lower() == "true"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "books.apps.BooksConfig",
    "accounts.apps.AccountsConfig",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "backend.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "backend.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/api/static/"
WHITENOISE_STATIC_PREFIX = "/static/"
FORCE_SCRIPT_NAME = os.environ.get("DJANGO_SCRIPT_NAME") or None
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REST_FRAMEWORK = {
    # Use the socket peer address, never an untrusted X-Forwarded-For header.
    "NUM_PROXIES": 0,
    "DEFAULT_THROTTLE_RATES": {
        "login": os.environ.get("DJANGO_LOGIN_RATE", "30/min"),
        "registration": os.environ.get("DJANGO_REGISTRATION_RATE", "10/hour"),
    },
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "CHECK_REVOKE_TOKEN": True,
    "TOKEN_REFRESH_SERIALIZER": "accounts.serializers.RevocableTokenRefreshSerializer",
}
AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# Production dependencies are explicit; development retains SQLite and memory cache.

if database_url := os.environ.get("DATABASE_URL"):
    db = urlparse(database_url)
    if db.scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured("DATABASE_URL must use PostgreSQL.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(db.path.lstrip("/")),
            "USER": unquote(db.username or ""),
            "PASSWORD": unquote(db.password or ""),
            "HOST": db.hostname,
            "PORT": db.port or 5432,
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {"sslmode": os.environ.get("POSTGRES_SSLMODE", "prefer")},
        }
    }
if redis_url := os.environ.get("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": redis_url,
            "KEY_PREFIX": "booktracker",
        }
    }

PUBLIC_URL = os.environ.get("DJANGO_PUBLIC_URL", "http://localhost:5173").rstrip("/")
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "1025"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", "false").lower() == "true"
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.environ.get(
    "DJANGO_DEFAULT_FROM_EMAIL", "Booktracker <noreply@example.com>"
)
PASSWORD_RESET_TIMEOUT = 3600
REQUIRE_EMAIL_VERIFICATION = (
    os.environ.get("DJANGO_REQUIRE_EMAIL_VERIFICATION", "true").lower() == "true"
)
AUTH_COOKIE_SECURE = not DEBUG
AUTH_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173" if DEBUG else ""
)
# Only enable when the application is reachable exclusively through the trusted gateway.
if os.environ.get("DJANGO_TRUST_PROXY", "false").lower() == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS += ["drf_spectacular"]
REST_FRAMEWORK.update(
    {
        "DEFAULT_AUTHENTICATION_CLASSES": ["accounts.authentication.SessionJWTAuthentication"],
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "EXCEPTION_HANDLER": "backend.errors.api_exception_handler",
    }
)
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update(
    {"email": os.environ.get("DJANGO_EMAIL_RATE", "5/hour"), "account": "30/hour"}
)
AUTH_PASSWORD_VALIDATORS[0]["OPTIONS"] = {"user_attributes": ["user_name", "email"]}
SPECTACULAR_SETTINGS = {
    "TITLE": "Booktracker API",
    "DESCRIPTION": "Private reading library and account API.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
MIDDLEWARE.insert(0, "backend.middleware.RequestLogMiddleware")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "backend.middleware.JSONLogFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "loggers": {
        "booktracker.requests": {"handlers": ["console"], "level": "INFO", "propagate": False}
    },
}
if sentry_dsn := os.environ.get("SENTRY_DSN"):
    import sentry_sdk

    from backend.observability import scrub_event

    sentry_sdk.init(
        dsn=sentry_dsn,
        send_default_pii=False,
        traces_sample_rate=0,
        before_send=scrub_event,
        include_local_variables=False,
        environment=os.environ.get("DJANGO_ENV", "development"),
        release=os.environ.get("APP_VERSION", "development"),
    )
AUTH_REDIS_URL = os.environ.get("REDIS_URL", "")

CSRF_FAILURE_VIEW = "backend.errors.csrf_failure"

SPECTACULAR_SETTINGS["POSTPROCESSING_HOOKS"] = [
    "drf_spectacular.hooks.postprocess_schema_enums",
    "accounts.schema.error_responses",
]

EMAIL_FILE_PATH = os.environ.get("DJANGO_EMAIL_FILE_PATH", str(BASE_DIR / "local-mail"))

INSTALLED_APPS += ["drf_spectacular_sidecar"]
MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")
SPECTACULAR_SETTINGS.update({"SWAGGER_UI_DIST": "SIDECAR", "SWAGGER_UI_FAVICON_HREF": "SIDECAR"})
