from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import CustomUser


class RefreshRotationTests(TestCase):
    def test_rotated_refresh_token_cannot_be_replayed(self):
        CustomUser.objects.create_user("rotate@example.com", "rotate", "Test-only-password-1")
        client = APIClient()
        login = client.post("/token/", {"email": "rotate@example.com", "password": "Test-only-password-1"})
        self.assertEqual(login.status_code, 200)
        old_refresh = login.data["refresh"]
        rotated = client.post("/token/refresh/", {"refresh": old_refresh})
        self.assertEqual(rotated.status_code, 200)
        self.assertNotEqual(rotated.data["refresh"], old_refresh)
        self.assertEqual(client.post("/token/refresh/", {"refresh": old_refresh}).status_code, 401)
        self.assertEqual(client.post("/token/refresh/", {"refresh": rotated.data["refresh"]}).status_code, 200)
