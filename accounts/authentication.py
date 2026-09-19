from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication


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
        if validated_token.get("session_version", 0) != user.session_version:
            raise AuthenticationFailed("This session has been revoked.")
        return user
