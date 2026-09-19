import math

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .throttles import LoginThrottle, ThrottleUnavailable


class AdminLoginThrottleMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method != "POST" or request.resolver_match.view_name != "admin:login":
            return None
        throttle = LoginThrottle()
        try:
            if throttle.allow_request(request, view_func):
                return None
        except ThrottleUnavailable as exc:
            response = JsonResponse({"detail": str(exc.detail)}, status=503)
        else:
            response = JsonResponse(
                {"detail": "Too many sign-in attempts. Please retry later."}, status=429
            )
            response["Retry-After"] = str(math.ceil(throttle.wait()))
        response["Cache-Control"] = "no-store"
        return response
