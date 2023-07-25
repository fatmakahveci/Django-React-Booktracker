import logging
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import CustomUser


class BaseBookTest(TestCase):
    def setUp(self) -> None:
        logger = logging.getLogger("django.request")
        logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        
        self.user_name = "user"
        self.email = "user@email.com"
        self.password = "reactSifresi1."
        user = CustomUser.objects.create_user(self.email, self.user_name, self.password)
        self.user = user

        self.client.post(
            "/register/",
            {
                "user_name": self.user_name,
                "email": self.email,
                "password": self.password,
            },
        )

        response = self.client.post(
            "/token/",
            {"email": self.email, "password": self.password},
        )
        self.token = str(response.data["access"])

        self.title = "title"
        self.author = "author"
        self.year = 1990
        self.finished = True

        self.client = APIClient()
