import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class ProductionEmailSecurityTests(SimpleTestCase):
    def settings_check(self, backend):
        env = {
            **os.environ,
            "DJANGO_ENV": "production",
            "DJANGO_DEBUG": "false",
            "DJANGO_SECRET_KEY": "isolated-settings-test-only-0123456789abcdefghijklmnopqrstuvwxyz",
            "DATABASE_URL": "postgresql://unused@127.0.0.1:1/unused",
            "REDIS_URL": "redis://127.0.0.1:1/0",
            "DJANGO_PUBLIC_URL": "https://example.com",
            "DJANGO_ALLOWED_HOSTS": "example.com",
            "SENTRY_DSN": "",
        }
        if backend is None:
            env.pop("DJANGO_EMAIL_BACKEND", None)
        else:
            env["DJANGO_EMAIL_BACKEND"] = f"django.core.mail.backends.{backend}.EmailBackend"
        return subprocess.run(
            [sys.executable, "-c", "import backend.settings"],
            env=env,
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_production_rejects_development_email_backends(self):
        for backend in (None, "console", "filebased", "locmem", "dummy"):
            with self.subTest(backend=backend):
                result = self.settings_check(backend)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Production requires a real email backend", result.stderr)

    def test_production_accepts_smtp_without_contacting_external_services(self):
        result = self.settings_check("smtp")
        self.assertEqual(result.returncode, 0, result.stderr)
