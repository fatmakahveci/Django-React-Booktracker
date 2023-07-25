from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["user_name"]

    objects = CustomUserManager()

    def __repr__(self) -> str:
        return f"""
        user_name: {self.user_name}
        email: {self.email}
        is_staff: {self.is_staff}
        is_active: {self.is_active}
        date_joined: {self.date_joined}
        """
