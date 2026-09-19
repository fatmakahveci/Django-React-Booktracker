"""Environment selection. Set DJANGO_ENV=production for deployed services."""

import os

if os.environ.get("DJANGO_ENV") == "production":
    from .production import *  # noqa: F403
elif os.environ.get("DJANGO_ENV") == "test":
    from .test import *  # noqa: F403
else:
    from .base import *  # noqa: F403
