"""Public, read-only JSON endpoints for the CSC 325 project."""
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def hello(request):
    return Response(
        {
            "message": "Hello from CSC 325!",
            "course": "CSC 325",
            "module": 8,
        }
    )


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "revision": settings.APP_REVISION})
