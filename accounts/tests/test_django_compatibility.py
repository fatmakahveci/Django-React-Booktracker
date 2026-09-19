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
            email="legacy@example.com",
            user_name="legacy",
            password=encoded,
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
            "admin@example.com",
            "admin",
            "Admin-test-password-1",
        )
        self.assertTrue(self.client.login(email=user.email, password="Admin-test-password-1"))
        for url in ("/admin/", "/admin/accounts/customuser/", "/admin/books/book/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)


class AdminAccountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = CustomUser.objects.create_superuser(
            "admin@example.com", "admin", "Admin-test-password-1"
        )
        cls.reader = CustomUser.objects.create_user(
            "reader@example.com", "reader", "Original-reader-password-73!"
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_admin_creates_user_with_normalized_email_and_hashed_password(self):
        self.assertEqual(self.client.get("/admin/accounts/customuser/add/").status_code, 200)
        password = "A-new-collection-password-83!"
        response = self.client.post(
            "/admin/accounts/customuser/add/",
            {
                "email": "NEW@example.com",
                "user_name": "new_reader",
                "password1": password,
                "password2": password,
                "is_active": "on",
                "email_verified": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(email="new@example.com")
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))
        self.assertEqual(
            APIClient().post("/token/", {"email": user.email, "password": password}).status_code,
            200,
        )

    def test_admin_profile_edit_cannot_replace_password_hash(self):
        original = self.reader.password
        response = self.client.post(
            f"/admin/accounts/customuser/{self.reader.pk}/change/",
            {
                "email": self.reader.email,
                "user_name": "updated_reader",
                "password": "attempted-raw-password",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.reader.refresh_from_db()
        self.assertEqual(self.reader.user_name, "updated_reader")
        self.assertEqual(self.reader.password, original)

    def test_admin_password_change_uses_password_policy_and_hashing(self):
        path = f"/admin/accounts/customuser/{self.reader.pk}/password/"
        response = self.client.post(path, {"password1": "123", "password2": "123"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["adminForm"].form.errors)
        password = "A-replacement-collection-password-91!"
        response = self.client.post(path, {"password1": password, "password2": password})
        self.assertEqual(response.status_code, 302)
        self.reader.refresh_from_db()
        self.assertTrue(self.reader.check_password(password))

    def test_admin_rejects_case_insensitive_duplicate_email(self):
        response = self.client.post(
            "/admin/accounts/customuser/add/",
            {
                "email": self.reader.email.upper(),
                "user_name": "another_reader",
                "password1": "A-new-collection-password-83!",
                "password2": "A-new-collection-password-83!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["adminform"].form.errors)
        self.assertFalse(CustomUser.objects.filter(user_name="another_reader").exists())
