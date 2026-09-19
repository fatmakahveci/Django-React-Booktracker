from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, user_name, password, **extra_fields):
        if not email:
            raise ValueError("You must have an e-mail address.")
        if not user_name:
            raise ValueError("You must have a username.")
        user = self.model(
            email=self.normalize_email(email).lower(), user_name=user_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_name, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(
            email=self.normalize_email(email).lower(),
            user_name=user_name,
            password=password,
            **extra_fields,
        )
