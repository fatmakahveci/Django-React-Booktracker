import logging

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser


class BaseBookTest(TestCase):
    def setUp(self) -> None:
        logger = logging.getLogger("django.request")
        self.addCleanup(logger.setLevel, logger.level)
        logger.setLevel(logging.ERROR)

        self.user_name = "user"
        self.email = "user@email.com"
        self.password = "reactSifresi1."
        self.user = CustomUser.objects.create_user(self.email, self.user_name, self.password)

        self.title = "title"
        self.author = "author"
        self.year = 1990
        self.finished = True

        self.client = APIClient()
