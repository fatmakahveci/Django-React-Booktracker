import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from unittest import skipUnless
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.core import mail
from django.core.cache import cache
from django.db import connection, connections
from django.test import TestCase, TransactionTestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import CustomUser
from books.models import Book


@override_settings(REQUIRE_EMAIL_VERIFICATION=True, AUTH_REDIS_URL="")
class BrowserAccountTests(TestCase):
    password = "Secluded-library-42!"

    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.csrf = self.client.get("/auth/csrf/").data["csrfToken"]
        self.client.credentials(HTTP_X_CSRFTOKEN=self.csrf)
        self.user = CustomUser.objects.create_user(
            "reader@example.com", "reader", self.password, email_verified=True
        )

    def login(self, client=None):
        client = client or self.client
        return client.post("/auth/login/", {"email": self.user.email, "password": self.password})

    def link(self):
        url = re.search(r"https?://\S+", mail.outbox[-1].body).group()
        return {key: value[0] for key, value in parse_qs(urlparse(url).query).items()}

    def test_cookies_are_http_only_and_csrf_is_required_on_login_and_writes(self):
        self.client.credentials()
        self.assertEqual(self.login().status_code, 403)
        self.client.credentials(HTTP_X_CSRFTOKEN=self.csrf)
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access", response.data)
        self.assertTrue(response.cookies["bt_access"]["httponly"])
        self.assertTrue(response.cookies["bt_refresh"]["httponly"])
        self.assertEqual(response.cookies["bt_refresh"]["samesite"], "Lax")
        self.assertEqual(self.client.get("/auth/me/").status_code, 200)
        self.client.credentials()
        self.assertEqual(self.client.patch("/auth/me/", {"user_name": "unsafe"}).status_code, 403)
        self.assertEqual(self.client.post("/auth/refresh/").status_code, 403)
        self.assertEqual(self.client.post("/auth/logout/").status_code, 403)
        self.client.credentials(HTTP_X_CSRFTOKEN=self.csrf, HTTP_ORIGIN="https://evil.example")
        self.assertEqual(self.client.patch("/auth/me/", {"user_name": "unsafe"}).status_code, 403)

    @override_settings(AUTH_COOKIE_SECURE=True)
    def test_production_cookie_flags(self):
        response = self.login()
        self.assertTrue(response.cookies["bt_access"]["secure"])
        self.assertTrue(response.cookies["bt_refresh"]["secure"])

    def test_refresh_rotation_and_logout_reject_replay(self):
        self.login()
        first = self.client.cookies["bt_refresh"].value
        self.assertEqual(self.client.post("/auth/refresh/").status_code, 200)
        second = self.client.cookies["bt_refresh"].value
        self.assertNotEqual(first, second)
        self.client.cookies["bt_refresh"] = first
        self.assertEqual(self.client.post("/auth/refresh/").status_code, 401)
        self.client.cookies["bt_refresh"] = second
        self.assertEqual(self.client.post("/auth/logout/").status_code, 204)
        self.assertEqual(self.client.get("/auth/me/").status_code, 401)
        self.client.cookies["bt_refresh"] = second
        self.assertEqual(self.client.post("/auth/refresh/").status_code, 401)

    def test_registration_verification_and_single_use_link(self):
        data = {"email": "NEW@example.com", "user_name": "new_reader", "password": self.password}
        self.assertEqual(self.client.post("/auth/register/", data).status_code, 201)
        self.assertTrue(CustomUser.objects.filter(email="new@example.com").exists())
        self.assertIn(self.client.post("/auth/login/", data).status_code, (401, 403))
        link = self.link()
        self.assertEqual(self.client.post("/auth/email/verify/", link).status_code, 200)
        self.assertEqual(self.client.post("/auth/email/verify/", link).status_code, 400)
        self.assertEqual(self.client.post("/auth/login/", data).status_code, 200)

    def test_reset_is_generic_one_time_and_revokes_existing_session(self):
        self.login()
        old_access = self.client.cookies["bt_access"].value
        known = self.client.post("/auth/password/reset/", {"email": self.user.email})
        link = self.link()
        unknown = self.client.post("/auth/password/reset/", {"email": "absent@example.com"})
        self.assertEqual(known.data, unknown.data)
        self.assertEqual(len(mail.outbox), 1)
        body = {**link, "password": "A-different-long-password-84!"}
        self.assertEqual(self.client.post("/auth/password/reset/confirm/", body).status_code, 200)
        self.assertEqual(self.client.post("/auth/password/reset/confirm/", body).status_code, 400)
        self.client.cookies["bt_access"] = old_access
        self.assertEqual(self.client.get("/auth/me/").status_code, 401)

    def test_reset_link_expiry_and_invalid_user(self):
        self.client.post("/auth/password/reset/", {"email": self.user.email})
        link = self.link()
        with patch(
            "django.contrib.auth.tokens.PasswordResetTokenGenerator._now",
            return_value=datetime.now() + timedelta(hours=2),
        ):
            self.assertEqual(
                self.client.post(
                    "/auth/password/reset/confirm/", {**link, "password": self.password}
                ).status_code,
                400,
            )
        self.assertEqual(
            self.client.post(
                "/auth/email/verify/", {"uid": "invalid", "token": "invalid"}
            ).status_code,
            400,
        )

    def test_password_change_and_revoke_all_invalidate_access_and_refresh(self):
        for action, body in [
            ("password/change", {"current_password": self.password, "new_password": self.password}),
            ("sessions/revoke", {"password": self.password}),
        ]:
            with self.subTest(action=action):
                self.login()
                access, refresh = [
                    self.client.cookies[key].value for key in ("bt_access", "bt_refresh")
                ]
                self.assertEqual(self.client.post(f"/auth/{action}/", body).status_code, 200)
                self.client.cookies["bt_access"] = access
                self.assertEqual(self.client.get("/auth/me/").status_code, 401)
                self.client.cookies["bt_refresh"] = refresh
                self.assertEqual(self.client.post("/auth/refresh/").status_code, 401)

    def test_profile_and_account_deletion_require_current_password(self):
        self.login()
        self.assertEqual(
            self.client.patch("/auth/me/", {"user_name": "updated_reader"}).status_code, 200
        )
        Book.objects.create(user=self.user, title="Private notes", author="Reader", year=2026)
        self.assertEqual(
            self.client.delete("/auth/account/", {"password": "wrong"}).status_code, 400
        )
        self.assertTrue(CustomUser.objects.filter(pk=self.user.pk).exists())
        self.assertEqual(
            self.client.delete("/auth/account/", {"password": self.password}).status_code, 204
        )
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(Book.objects.exists())


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row locking integration test")
@override_settings(REQUIRE_EMAIL_VERIFICATION=False, AUTH_REDIS_URL="")
class RefreshConcurrencyTests(TransactionTestCase):
    def test_same_refresh_cookie_cannot_rotate_twice_concurrently(self):
        from accounts.serializers import MyTokenObtainPairSerializer

        user = CustomUser.objects.create_user(
            "concurrency@example.com", "concurrent_reader", "test-only-password"
        )
        token = str(MyTokenObtainPairSerializer.get_token(user))

        def refresh(_):
            try:
                client = APIClient()
                client.cookies["bt_refresh"] = token
                return client.post("/auth/refresh/").status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(refresh, range(2)))
        self.assertEqual(statuses, [200, 401])
