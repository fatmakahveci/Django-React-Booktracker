from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerSplitView
from rest_framework import routers

from backend.health import live, ready

router = routers.DefaultRouter()

urlpatterns = [
    path("health/live/", live),
    path("health/ready/", ready),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerSplitView.as_view(url_name="schema"), name="api-docs"),
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("books/", include("books.urls")),
    path("", include("accounts.urls")),
]
