from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
from re import match


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "user_name"]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["email"] = user.email
        token["user_name"] = user.user_name

        return token


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "user_name", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        USER_NAME_PATTERN = "(\w[.-]?){4,24}$"
        EMAIL_PATTERN = "\w+([.-]?\w+)*@\w+([.-]?\w+)*(.\w{2,3})+"
        PASSWORD_PATTERN = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%.]).{8,24}$"

        user_name = attrs.get("user_name", "")
        if not match(USER_NAME_PATTERN, user_name):
            raise serializers.ValidationError("Username is not valid.")

        email = attrs.get("email", "")
        if not match(EMAIL_PATTERN, email):
            raise serializers.ValidationError("Email is not valid.")

        password = attrs.get("password", "")
        if not match(PASSWORD_PATTERN, password):
            raise serializers.ValidationError("Password is not valid.")

        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def save(self):
        user = CustomUser(
            email=self.validated_data["email"],
            user_name=self.validated_data["user_name"],
            password=None,
        )
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        return user
