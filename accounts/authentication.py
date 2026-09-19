from contextlib import contextmanager

from django.conf import settings
from django.db import transaction
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import CustomUser


@contextmanager
def locked_user(user_id):
    with transaction.atomic():
        try:
            user = CustomUser.objects.select_for_update().get(pk=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("This account is no longer available.") from None
        yield user


@contextmanager
def locked_authenticated_user(request):
    with locked_user(request.user.pk) as user:
        # Authentication may precede a concurrent password change or session revocation.
        if request.auth is not None:
            SessionJWTAuthentication().get_user(request.auth)
        request.user = user
        yield user


class SessionJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        if self.get_header(request) is not None:
            return super().authenticate(request)
        token = request.COOKIES.get("bt_access")
        if not token:
            return None
        check = CSRFCheck(lambda req: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise PermissionDenied("CSRF verification failed.")
        validated = self.get_validated_token(token)
        return self.get_user(validated), validated

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if settings.REQUIRE_EMAIL_VERIFICATION and not user.email_verified:
            raise AuthenticationFailed("Verify your email before continuing.")
        if validated_token.get("session_version", 0) != user.session_version:
            raise AuthenticationFailed("This session has been revoked.")
        return user
