from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        data = response.data
        message = (
            data.get("detail", "Check the highlighted fields.")
            if isinstance(data, dict)
            else "Invalid request."
        )
        response.data = {
            "error": {
                "code": getattr(exc, "default_code", "request_error"),
                "message": str(message),
                "fields": data,
            },
            "detail": str(message),
        }
    return response


def csrf_failure(request, reason=""):
    from django.http import JsonResponse

    message = "CSRF verification failed. Reload the page and try again."
    return JsonResponse(
        {"error": {"code": "csrf_failed", "message": message, "fields": {}}, "detail": message},
        status=403,
    )
