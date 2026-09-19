from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import serializers

from .account_serializers import ProfileSerializer


class SessionJWTScheme(OpenApiAuthenticationExtension):
    target_class = "accounts.authentication.SessionJWTAuthentication"
    name = ["cookieAuth", "bearerAuth"]

    def get_security_requirement(self, auto_schema):
        return [{"cookieAuth": []}, {"bearerAuth": []}]

    def get_security_definition(self, auto_schema):
        return [
            {
                "type": "apiKey",
                "in": "cookie",
                "name": "bt_access",
                "description": "Unsafe cookie requests also require X-CSRFToken from /auth/csrf/.",
            },
            {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
        ]


class EmptySerializer(serializers.Serializer):
    pass


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()


class CSRFSerializer(serializers.Serializer):
    csrfToken = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    user = ProfileSerializer()


class SummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    finished = serializers.IntegerField()
    unfinished = serializers.IntegerField()


def error_responses(result, generator, request, public):
    result["components"]["schemas"]["APIError"] = {
        "type": "object",
        "required": ["error", "detail"],
        "properties": {
            "detail": {"type": "string"},
            "error": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "fields": {"type": "object", "additionalProperties": True},
                },
            },
        },
    }
    for path in result["paths"].values():
        for method, operation in path.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            for status in ("400", "401", "403", "404", "429", "503"):
                operation["responses"].setdefault(
                    status,
                    {
                        "description": "Request failed. 429 includes Retry-After seconds.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/APIError"}
                            }
                        },
                    },
                )
    return result
