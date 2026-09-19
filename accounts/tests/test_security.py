from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts.models import CustomUser


class CredentialSecurityTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            "security@example.com", "security_reader", "OriginalPassword42!"
        )
        self.client = APIClient()
        response = self.client.post(
            "/token/",
            {
                "email": self.user.email,
                "password": "OriginalPassword42!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.tokens = response.data

    def change_password(self):
        self.user.set_password("ReplacementPassword73!")
        self.user.save(update_fields=["password"])

    def test_password_change_revokes_access_token(self):
        self.change_password()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")
        self.assertEqual(self.client.get("/books/").status_code, 401)

    def test_password_change_revokes_refresh_token(self):
        self.change_password()
        response = self.client.post("/token/refresh/", {"refresh": self.tokens["refresh"]})
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access", response.data)

    def test_deleted_account_refresh_is_rejected_without_server_error(self):
        self.user.delete()
        response = self.client.post("/token/refresh/", {"refresh": self.tokens["refresh"]})
        self.assertEqual(response.status_code, 401)

    def test_new_login_after_password_change_works(self):
        self.change_password()
        response = self.client.post(
            "/token/",
            {
                "email": self.user.email,
                "password": "ReplacementPassword73!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(self.client.get("/books/").status_code, 200)
        self.assertEqual(
            self.client.post(
                "/token/refresh/",
                {
                    "refresh": response.data["refresh"],
                },
            ).status_code,
            200,
        )


class RegistrationPasswordPolicyTests(TestCase):
    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {"min_length": 16},
            }
        ]
    )
    def test_registration_enforces_configured_password_policy(self):
        response = APIClient().post(
            "/register/",
            {
                "email": "policy@example.com",
                "user_name": "policy_reader",
                "password": "ShortPass42!",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CustomUser.objects.filter(email="policy@example.com").exists())

    def test_registration_rejects_password_similar_to_email(self):
        response = APIClient().post(
            "/register/",
            {
                "email": "BookReader42@example.com",
                "user_name": "new_reader",
                "password": "BookReader42!",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CustomUser.objects.filter(email="BookReader42@example.com").exists())
