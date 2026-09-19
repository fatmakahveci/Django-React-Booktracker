from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import CustomUser


def check_password(value, user=None):
    try:
        validate_password(value, user)
    except ValidationError as exc:
        raise serializers.ValidationError(exc.messages) from exc
    return value


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "user_name", "email_verified", "date_joined")
        read_only_fields = ("id", "email", "email_verified", "date_joined")

    def validate_user_name(self, value):
        value = value.strip()
        if len(value) < 4:
            raise serializers.ValidationError("Use at least four characters.")
        return value


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": "Incorrect password."})
        check_password(attrs["new_password"], user)
        return attrs


class PasswordConfirmationSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")
        return value


class LinkTokenSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=128)
    token = serializers.CharField(max_length=256)


class ResetPasswordSerializer(LinkTokenSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
