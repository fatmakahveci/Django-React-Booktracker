import ipaddress
import json
import logging
import time
import uuid

from django.conf import settings

logger = logging.getLogger("booktracker.requests")


class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "level": record.levelname,
                "event": record.getMessage(),
                **getattr(record, "request_meta", {}),
            }
        )


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "SECURE_PROXY_SSL_HEADER", None) and request.META.get(
            "HTTP_X_REAL_IP"
        ):
            try:
                request.META["REMOTE_ADDR"] = str(
                    ipaddress.ip_address(request.META["HTTP_X_REAL_IP"])
                )
            except ValueError:
                pass
        started = time.monotonic()
        request_id = uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        if request.path_info.startswith(("/auth/", "/books/", "/token/")):
            response["Cache-Control"] = "no-store"
        response["Referrer-Policy"] = "same-origin"
        # Paths can contain reset tokens. Log only the route template, never query/body/cookies.
        route = getattr(request.resolver_match, "route", "unresolved")
        logger.info(
            "http_request",
            extra={
                "request_meta": {
                    "request_id": request_id,
                    "method": request.method,
                    "route": route,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                }
            },
        )
        return response
