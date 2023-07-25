import logging
from django.test import TestCase
from rest_framework.test import APIClient


class BaseAccountTest(TestCase):
    def setUp(self) -> None:        
        logger = logging.getLogger("django.request")
        logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        self.user_name = "user"
        self.email = "user@email.com"
        self.password = "reactSifresi1."

        self.client = APIClient()
