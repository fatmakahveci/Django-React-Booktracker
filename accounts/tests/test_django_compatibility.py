from django.contrib.auth.hashers import PBKDF2PasswordHasher, identify_hasher
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser


class DjangoUpgradeCompatibilityTests(TestCase):
    def test_existing_pbkdf2_password_can_login_and_is_upgraded(self):
        password = "Legacy-account-password-1"
        hasher = PBKDF2PasswordHasher()
        legacy_iterations = 1_000_000
        encoded = hasher.encode(password, hasher.salt(), iterations=legacy_iterations)
        user = CustomUser.objects.create(
            email="legacy@example.com", user_name="legacy", password=encoded,
        )

        response = APIClient().post("/token/", {"email": user.email, "password": password})

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        user.refresh_from_db()
        self.assertTrue(user.check_password(password))
        decoded = identify_hasher(user.password).decode(user.password)
        self.assertEqual(decoded["iterations"], hasher.iterations)
        self.assertGreater(decoded["iterations"], legacy_iterations)

    def test_admin_authentication_and_custom_user_pages(self):
        user = CustomUser.objects.create_superuser(
            "admin@example.com", "admin", "Admin-test-password-1",
        )
        self.assertTrue(self.client.login(email=user.email, password="Admin-test-password-1"))
        for url in ("/admin/", "/admin/accounts/customuser/", "/admin/books/book/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
