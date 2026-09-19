from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .account_serializers import (
    EmailSerializer,
    LinkTokenSerializer,
    PasswordChangeSerializer,
    PasswordConfirmationSerializer,
    ProfileSerializer,
    ResetPasswordSerializer,
    check_password,
)
from .models import CustomUser
from .schema import CSRFSerializer, DetailSerializer, EmptySerializer, LoginResponseSerializer
from .serializers import (
    MyTokenObtainPairSerializer,
    RegistrationSerializer,
    RevocableTokenRefreshSerializer,
)
from .throttles import AccountThrottle, EmailThrottle, LoginThrottle, RegistrationThrottle
from .tokens import email_verification_token


def clear_auth(response):
    for name in ("bt_access", "bt_refresh"):
        response.delete_cookie(name, path="/", samesite=settings.AUTH_COOKIE_SAMESITE)
    return response


def set_auth(response, data):
    for name, key, lifetime in (
        ("bt_access", "access", "ACCESS_TOKEN_LIFETIME"),
        ("bt_refresh", "refresh", "REFRESH_TOKEN_LIFETIME"),
    ):
        response.set_cookie(
            name,
            data[key],
            max_age=int(settings.SIMPLE_JWT[lifetime].total_seconds()),
            httponly=True,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            path="/",
        )
    response["Cache-Control"] = "no-store"
    return response


def send_link(user, generator, route, subject):
    query = urlencode(
        {"uid": urlsafe_base64_encode(force_bytes(user.pk)), "token": generator.make_token(user)}
    )
    send_mail(
        subject,
        f"Open this link to continue:\n{settings.PUBLIC_URL}/{route}?{query}\n\nIf you did not request this, ignore this email.",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )


def user_from_link(attrs, generator):
    try:
        uid = urlsafe_base64_decode(attrs["uid"]).decode()
        # Call inside transaction.atomic(): concurrent requests must recheck the locked row.
        user = CustomUser.objects.select_for_update().get(pk=uid, is_active=True)
    except (ValueError, TypeError, OverflowError, UnicodeDecodeError, CustomUser.DoesNotExist):
        raise ValidationError("The link is invalid or has expired.") from None
    if not generator.check_token(user, attrs["token"]):
        raise ValidationError("The link is invalid or has expired.")
    return user


@method_decorator(csrf_protect, name="dispatch")
class PublicAction(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = EmptySerializer

    def get_authenticate_header(self, request):
        return "Bearer"


@method_decorator(ensure_csrf_cookie, name="dispatch")
@extend_schema(responses=CSRFSerializer)
class CSRFView(PublicAction):
    def get(self, request):
        response = Response({"csrfToken": get_token(request)})
        response["Cache-Control"] = "no-store"
        return response


@extend_schema(responses=LoginResponseSerializer)
class BrowserLoginView(PublicAction):
    serializer_class = MyTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return set_auth(
            Response({"user": ProfileSerializer(serializer.user).data}), serializer.validated_data
        )


@extend_schema(responses={201: DetailSerializer})
class BrowserRegisterView(PublicAction):
    serializer_class = RegistrationSerializer
    throttle_classes = [RegistrationThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_link(user, email_verification_token, "verify-email", "Verify your Booktracker email")
        return Response(
            {"detail": "Check your email to verify your account."}, status=status.HTTP_201_CREATED
        )


@extend_schema(responses=DetailSerializer)
class BrowserRefreshView(PublicAction):
    def post(self, request):
        serializer = RevocableTokenRefreshSerializer(
            data={"refresh": request.COOKIES.get("bt_refresh", "")}
        )
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(str(exc)) from exc
        return set_auth(Response({"detail": "Session renewed."}), serializer.validated_data)


@extend_schema(responses={204: None})
class BrowserLogoutView(PublicAction):
    def post(self, request):
        if refresh := request.COOKIES.get("bt_refresh"):
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass
        return clear_auth(Response(status=status.HTTP_204_NO_CONTENT))


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


@extend_schema(responses=DetailSerializer)
class ChangePasswordView(GenericAPIView):
    throttle_classes = [AccountThrottle]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return clear_auth(Response({"detail": "Password changed. Sign in again."}))


@extend_schema(responses=DetailSerializer)
class LogoutAllView(GenericAPIView):
    throttle_classes = [AccountThrottle]
    serializer_class = PasswordConfirmationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CustomUser.objects.filter(pk=request.user.pk).update(
            session_version=F("session_version") + 1
        )
        return clear_auth(Response({"detail": "All sessions revoked."}))


@extend_schema(responses={204: None})
class DeleteAccountView(GenericAPIView):
    throttle_classes = [AccountThrottle]
    serializer_class = PasswordConfirmationSerializer

    def delete(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            # Outstanding JWT records otherwise survive as SET_NULL and retain identity claims.
            OutstandingToken.objects.filter(user=request.user).delete()
            request.user.delete()
        return clear_auth(Response(status=status.HTTP_204_NO_CONTENT))


@extend_schema(responses=DetailSerializer)
class PasswordResetRequestView(PublicAction):
    serializer_class = EmailSerializer
    throttle_classes = [EmailThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.filter(
            email__iexact=serializer.validated_data["email"], is_active=True
        ).first()
        if user:
            send_link(
                user, default_token_generator, "reset-password", "Reset your Booktracker password"
            )
        return Response({"detail": "If the account exists, a reset link has been sent."})


@extend_schema(responses=DetailSerializer)
class PasswordResetConfirmView(PublicAction):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attrs = serializer.validated_data
        with transaction.atomic():
            user = user_from_link(attrs, default_token_generator)
            user.set_password(check_password(attrs["password"], user))
            user.save(update_fields=["password"])
        return clear_auth(Response({"detail": "Password reset. Sign in with your new password."}))


@extend_schema(responses=DetailSerializer)
class VerifyEmailView(PublicAction):
    serializer_class = LinkTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = user_from_link(serializer.validated_data, email_verification_token)
            user.email_verified = True
            user.save(update_fields=["email_verified"])
        return Response({"detail": "Email verified. You can now sign in."})


@extend_schema(responses=DetailSerializer)
class ResendVerificationView(PasswordResetRequestView):
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.filter(
            email__iexact=serializer.validated_data["email"], is_active=True, email_verified=False
        ).first()
        if user:
            send_link(
                user, email_verification_token, "verify-email", "Verify your Booktracker email"
            )
        return Response({"detail": "If verification is needed, a link has been sent."})
