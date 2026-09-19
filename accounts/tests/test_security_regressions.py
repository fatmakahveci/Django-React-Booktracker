from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db import connection, connections
from django.test import Client, TestCase, TransactionTestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from accounts.authentication import SessionJWTAuthentication
from accounts.models import CustomUser
from accounts.serializers import MyTokenObtainPairSerializer
from accounts.throttles import LoginThrottle, RefreshThrottle, ThrottleUnavailable


class AccountWriteSecurityTests(TestCase):
    password = "Original-reading-password-71!"

    def setUp(self):
        cache.clear()
        self.user = CustomUser.objects.create_user(
            "race@example.com", "race_reader", self.password, email_verified=True
        )
        self.refresh = str(MyTokenObtainPairSerializer.get_token(self.user))
        self.access = str(MyTokenObtainPairSerializer.get_token(self.user).access_token)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_revocation_during_authentication_blocks_account_writes(self):
        actions = (
            ("patch", "/auth/me/", {"user_name": "changed_reader"}),
            (
                "post",
                "/auth/password/change/",
                {"current_password": self.password, "new_password": "Unwanted-replacement-42!"},
            ),
            ("post", "/auth/sessions/revoke/", {"password": self.password}),
            ("delete", "/auth/account/", {"password": self.password}),
        )
        original_get_user = SessionJWTAuthentication.get_user
        for method, path, body in actions:
            with self.subTest(path=path):
                CustomUser.objects.filter(pk=self.user.pk).update(
                    password=make_password(self.password), session_version=0
                )
                self.user.refresh_from_db()
                token = MyTokenObtainPairSerializer.get_token(self.user)
                self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
                replacement = make_password("Owner-recovery-password-83!")
                authenticated = False

                def revoke_after_authentication(auth, validated_token):
                    nonlocal authenticated
                    user = original_get_user(auth, validated_token)
                    if not authenticated:
                        authenticated = True
                        # Reproduce a revocation committed after authentication but before saving.
                        CustomUser.objects.filter(pk=user.pk).update(
                            password=replacement, session_version=1
                        )
                    return user

                with patch.object(
                    SessionJWTAuthentication, "get_user", revoke_after_authentication
                ):
                    response = getattr(self.client, method)(path, body)
                self.assertEqual(response.status_code, 401)
                self.user.refresh_from_db()
                self.assertEqual(self.user.password, replacement)
                self.assertEqual(self.user.session_version, 1)
                self.assertEqual(self.user.user_name, "race_reader")

    def test_profile_write_cannot_recreate_an_account_deleted_after_authentication(self):
        original = SessionJWTAuthentication.get_user

        def delete_after_authentication(auth, token):
            user = original(auth, token)
            CustomUser.objects.filter(pk=user.pk).delete()
            return user

        with patch.object(SessionJWTAuthentication, "get_user", delete_after_authentication):
            response = self.client.patch("/auth/me/", {"user_name": "resurrected_reader"})
        self.assertEqual(response.status_code, 401)
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())

    def test_logout_cannot_restore_tokens_purged_by_account_deletion(self):
        self.assertEqual(
            self.client.delete("/auth/account/", {"password": self.password}).status_code, 204
        )
        for path in ("/auth/logout/", "/logout/"):
            with self.subTest(path=path):
                client = APIClient()
                client.cookies["bt_refresh"] = self.refresh
                response = client.post(path, {"refresh": self.refresh})
                self.assertIn(response.status_code, (200, 204))
                self.assertFalse(OutstandingToken.objects.exists())

    def test_deleted_token_records_cannot_be_recreated_by_refresh(self):
        OutstandingToken.objects.filter(user=self.user).delete()
        for path in ("/auth/refresh/", "/token/refresh/"):
            with self.subTest(path=path):
                self.client.cookies["bt_refresh"] = self.refresh
                response = self.client.post(path, {"refresh": self.refresh})
                self.assertEqual(response.status_code, 401)
                self.assertFalse(OutstandingToken.objects.exists())

    def test_refresh_endpoints_share_a_request_limit(self):
        with patch.object(RefreshThrottle, "rate", "2/min", create=True):
            self.assertEqual(self.client.post("/auth/refresh/").status_code, 400)
            self.assertEqual(self.client.post("/token/refresh/").status_code, 400)
            response = self.client.post("/auth/refresh/")
            self.assertEqual(response.status_code, 429)
            self.assertGreater(int(response["Retry-After"]), 0)

    @override_settings(REQUIRE_EMAIL_VERIFICATION=True)
    def test_existing_sessions_cannot_bypass_email_verification(self):
        CustomUser.objects.filter(pk=self.user.pk).update(email_verified=False)
        self.assertEqual(self.client.get("/auth/me/").status_code, 401)
        for path in ("/auth/refresh/", "/token/refresh/"):
            with self.subTest(path=path):
                self.client.cookies["bt_refresh"] = self.refresh
                self.assertEqual(self.client.post(path, {"refresh": self.refresh}).status_code, 401)

    def test_sign_in_cannot_issue_tokens_for_stale_credentials(self):
        CustomUser.objects.filter(pk=self.user.pk).update(
            password=make_password("Replacement-reading-password-83!")
        )
        original_count = OutstandingToken.objects.count()
        from rest_framework.exceptions import AuthenticationFailed

        with self.assertRaises(AuthenticationFailed):
            MyTokenObtainPairSerializer.get_token(self.user)
        self.assertEqual(OutstandingToken.objects.count(), original_count)


@override_settings(AUTH_REDIS_URL="", SECURE_PROXY_SSL_HEADER=None)
class AdminLoginSecurityTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.client = Client(enforce_csrf_checks=True)
        self.client.get("/admin/login/")
        self.csrf = self.client.cookies["csrftoken"].value

    def login(self, **headers):
        return self.client.post(
            "/admin/login/",
            {"username": "absent@example.com", "password": "wrong"},
            HTTP_X_CSRFTOKEN=self.csrf,
            **headers,
        )

    def test_admin_password_attempts_are_limited_by_peer_address(self):
        with patch.object(LoginThrottle, "rate", "2/min", create=True):
            self.assertEqual(self.login(HTTP_X_FORWARDED_FOR="192.0.2.1").status_code, 200)
            self.assertEqual(self.login(HTTP_X_FORWARDED_FOR="192.0.2.2").status_code, 200)
            response = self.login(HTTP_X_FORWARDED_FOR="192.0.2.3")
            self.assertEqual(response.status_code, 429)
            self.assertGreater(int(response["Retry-After"]), 0)
            self.assertEqual(self.login(REMOTE_ADDR="192.0.2.4").status_code, 200)

    def test_admin_authentication_fails_closed_when_throttling_is_unavailable(self):
        with patch.object(LoginThrottle, "allow_request", side_effect=ThrottleUnavailable):
            self.assertEqual(self.login().status_code, 503)


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL row locks")
class AccountWriteConcurrencyTests(TransactionTestCase):
    password = "Original-reading-password-71!"

    def setUp(self):
        cache.clear()
        self.user = CustomUser.objects.create_user(
            "parallel@example.com", "parallel_reader", self.password, email_verified=True
        )
        token = MyTokenObtainPairSerializer.get_token(self.user)
        self.refresh = str(token)
        self.access = str(token.access_token)

    def concurrent_requests(self, actions):
        barrier = Barrier(len(actions))

        def send(action):
            client = APIClient()
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
            client.cookies["bt_refresh"] = self.refresh
            try:
                barrier.wait(timeout=10)
                method, path, data = action
                return getattr(client, method)(path, data).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=len(actions)) as pool:
            return list(pool.map(send, actions))

    def test_account_deletion_and_refresh_leave_no_token_records(self):
        deleted, refreshed = self.concurrent_requests(
            (
                ("delete", "/auth/account/", {"password": self.password}),
                ("post", "/auth/refresh/", {}),
            )
        )
        self.assertEqual(deleted, 204)
        self.assertIn(refreshed, (200, 401))
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())
        self.assertFalse(OutstandingToken.objects.exists())

    def test_profile_update_cannot_roll_back_a_concurrent_password_change(self):
        password = "Replacement-reading-password-83!"
        changed, profile = self.concurrent_requests(
            (
                (
                    "post",
                    "/auth/password/change/",
                    {"current_password": self.password, "new_password": password},
                ),
                ("patch", "/auth/me/", {"user_name": "updated_reader"}),
            )
        )
        self.assertEqual(changed, 200)
        self.assertIn(profile, (200, 401))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(password))
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        self.assertEqual(client.get("/auth/me/").status_code, 401)
