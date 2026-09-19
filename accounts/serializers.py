from re import match

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from accounts.authentication import SessionJWTAuthentication

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "user_name"]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        attrs["email"] = attrs["email"].strip().lower()
        data = super().validate(attrs)
        if settings.REQUIRE_EMAIL_VERIFICATION and not self.user.email_verified:
            raise AuthenticationFailed("Verify your email before signing in.")
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["session_version"] = user.session_version
        token["email"] = user.email
        token["user_name"] = user.user_name

        return token


class RevocableTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])
        # Serialize rotations of the same refresh token across PostgreSQL workers.
        with transaction.atomic():
            OutstandingToken.objects.select_for_update().filter(jti=refresh["jti"]).first()
            SessionJWTAuthentication().get_user(refresh)
            return super().validate(attrs)


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "user_name", "password")
        extra_kwargs = {
            "password": {"write_only": True, "trim_whitespace": False, "max_length": 128}
        }

    def validate_email(self, value):
        value = value.strip().lower()
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_user_name(self, value):
        if not match(r"[\w.-]{4,24}\Z", value):
            raise serializers.ValidationError(
                "Use 4–24 letters, numbers, dots, underscores or hyphens."
            )
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
