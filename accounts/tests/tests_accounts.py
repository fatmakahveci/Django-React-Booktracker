from accounts.models import CustomUser
from accounts.tests.base import BaseAccountTest
from rest_framework import status


class AccountAPITest(BaseAccountTest):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_get_token_url(self):
        """
        Get token url, return status code 200
        """
        response = self.client.get("/token/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_token_with_invalid_password(self):
        """
        Do not get token if password is invalid, return status code 401
        """
        response = self.client.post(
            "/token/",
            {"email": self.email, "password": "wrong_password"},
        )

        self.assertEqual(
            status.HTTP_401_UNAUTHORIZED,
            response.status_code,
            msg="Token for unauthorized user has been created. Password is invalid.",
        )

    def test_get_token_with_invalid_email(self):
        """
        Do not get token if email is invalid, return status code 401
        """
        response = self.client.post(
            "/token/",
            {"email": "wrong_email", "password": self.password},
        )

        self.assertEqual(
            status.HTTP_401_UNAUTHORIZED,
            response.status_code,
            msg="Token for unauthorized user has been created. Email is invalid.",
        )

    def test_register_with_valid_credentials(self):
        """
        Register with valid credentials, return status code 201
        """
        response = self.client.post(
            "/register/",
            {
                "user_name": self.user_name,
                "email": self.email,
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_token_with_valid_credentials(self):
        """
        Get token if credentials are invalid, return status code 200
        """
        CustomUser.objects.create_user(self.email, self.user_name, self.password)
        response = self.client.post(
            "/token/",
            {"email": self.email, "password": self.password},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["access"])
