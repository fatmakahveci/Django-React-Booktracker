import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

if DEBUG:  # noqa: F405
    raise ImproperlyConfigured("DJANGO_DEBUG must be false in production.")
DEBUG = False
for required in ("DATABASE_URL", "REDIS_URL", "DJANGO_PUBLIC_URL", "DJANGO_ALLOWED_HOSTS"):
    if not os.environ.get(required):
        raise ImproperlyConfigured(f"Production requires {required}.")
if not os.environ["DJANGO_PUBLIC_URL"].startswith("https://"):
    raise ImproperlyConfigured("Production DJANGO_PUBLIC_URL must use HTTPS.")
