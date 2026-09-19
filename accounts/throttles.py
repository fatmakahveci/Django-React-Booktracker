from rest_framework.throttling import SimpleRateThrottle


class ClientIPThrottle(SimpleRateThrottle):
    """Apply limits even when a caller already has a valid access token."""

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class LoginThrottle(ClientIPThrottle):
    scope = "login"


class RegistrationThrottle(ClientIPThrottle):
    scope = "registration"
