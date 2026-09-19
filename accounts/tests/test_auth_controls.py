from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from accounts.throttles import LoginThrottle, RegistrationThrottle


class AuthRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.client = APIClient()

    def test_login_limit_cannot_be_bypassed_with_forwarded_headers(self):
        with patch.object(LoginThrottle, "rate", "2/min", create=True):
            for value in ("192.0.2.1", "192.0.2.2"):
                response = self.client.post("/token/", {}, HTTP_X_FORWARDED_FOR=value)
                self.assertEqual(response.status_code, 400)
            response = self.client.post("/token/", {}, HTTP_X_FORWARDED_FOR="192.0.2.3")
            self.assertEqual(response.status_code, 429)
            self.assertGreater(int(response["Retry-After"]), 0)
            self.assertEqual(
                self.client.post("/token/", {}, REMOTE_ADDR="192.0.2.4").status_code, 400
            )

    def test_login_limit_expires_and_does_not_block_registration(self):
        with patch.object(LoginThrottle, "rate", "1/min", create=True):
            with patch.object(LoginThrottle, "timer", return_value=1000):
                self.assertEqual(self.client.post("/token/", {}).status_code, 400)
                self.assertEqual(self.client.post("/token/", {}).status_code, 429)
                self.assertEqual(self.client.post("/register/", {}).status_code, 400)
            with patch.object(LoginThrottle, "timer", return_value=1061):
                self.assertEqual(self.client.post("/token/", {}).status_code, 400)

    def test_registration_is_limited_even_for_authenticated_callers(self):
        user = CustomUser.objects.create_user("limit@example.com", "limited", "Password42!")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}"
        )
        with patch.object(RegistrationThrottle, "rate", "1/hour", create=True):
            self.assertEqual(self.client.post("/register/", {}).status_code, 400)
            response = self.client.post("/register/", {})
            self.assertEqual(response.status_code, 429)
            self.assertGreater(int(response["Retry-After"]), 0)


class LogoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            "logout@example.com", "logout_reader", "Password42!"
        )
        self.token = RefreshToken.for_user(self.user)

    def test_logout_revokes_only_the_submitted_refresh_token(self):
        other_session = RefreshToken.for_user(self.user)
        # No access token is required, so an expired access token cannot block logout.
        response = self.client.post("/logout/", {"refresh": str(self.token)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.post("/token/refresh/", {"refresh": str(self.token)}).status_code, 401
        )
        self.assertEqual(
            self.client.post("/token/refresh/", {"refresh": str(other_session)}).status_code, 200
        )

    def test_invalid_or_missing_refresh_cannot_revoke_another_session(self):
        self.assertEqual(self.client.post("/logout/", {}).status_code, 400)
        self.assertEqual(self.client.post("/logout/", {"refresh": "invalid"}).status_code, 401)
        self.assertEqual(
            self.client.post("/token/refresh/", {"refresh": str(self.token)}).status_code, 200
        )

    def test_repeated_logout_keeps_token_revoked(self):
        self.assertEqual(
            self.client.post("/logout/", {"refresh": str(self.token)}).status_code, 200
        )
        self.assertEqual(
            self.client.post("/logout/", {"refresh": str(self.token)}).status_code, 401
        )
        self.assertEqual(
            self.client.post("/token/refresh/", {"refresh": str(self.token)}).status_code, 401
        )
