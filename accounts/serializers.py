from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import (
    TokenBlacklistSerializer,
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from accounts.authentication import SessionJWTAuthentication, locked_user

from .models import CustomUser
from .validators import validate_user_name


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        attrs["email"] = attrs["email"].strip().lower()
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        with locked_user(user.pk) as current:
            if current.password != user.password:
                raise AuthenticationFailed("Credentials changed. Sign in again.")
            if settings.REQUIRE_EMAIL_VERIFICATION and not current.email_verified:
                raise AuthenticationFailed("Verify your email before signing in.")
            token = super().get_token(current)
            token["session_version"] = current.session_version
            token["email"] = current.email
            token["user_name"] = current.user_name
            return token


class RevocableTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        # Always lock the user before token rows, matching account deletion's lock order.
        with locked_user(refresh[api_settings.USER_ID_CLAIM]) as user:
            outstanding = (
                OutstandingToken.objects.select_for_update()
                .filter(jti=refresh["jti"], user=user)
                .first()
            )
            if outstanding is None:
                raise InvalidToken("This session is no longer available.")
            SessionJWTAuthentication().get_user(refresh)
            return super().validate(attrs)


class ExistingTokenBlacklistSerializer(TokenBlacklistSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        with transaction.atomic():
            token = OutstandingToken.objects.select_for_update().filter(jti=refresh["jti"]).first()
            # Logout must not recreate identity-bearing records after account deletion.
            if token is not None:
                BlacklistedToken.objects.get_or_create(token=token)
        return {}


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "user_name", "password")
        extra_kwargs = {
            "user_name": {"min_length": 4, "max_length": 24},
            "password": {"write_only": True, "trim_whitespace": False, "max_length": 128},
        }

    def validate_email(self, value):
        value = value.strip().lower()
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_user_name(self, value):
        validate_user_name(value)
        return value

    def validate(self, attrs):
        try:
            validate_password(
                attrs["password"],
                user=CustomUser(email=attrs["email"], user_name=attrs["user_name"]),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
