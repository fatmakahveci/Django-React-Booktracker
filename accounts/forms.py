from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import CustomUser
from .validators import validate_user_name


class AccountIdentityMixin:
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_user_name(self):
        value = self.cleaned_data["user_name"]
        validate_user_name(value)
        return value


class CustomUserCreationForm(AccountIdentityMixin, BaseUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "user_name")


class CustomUserChangeForm(AccountIdentityMixin, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
