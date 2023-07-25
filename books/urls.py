from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'', views.BookViewSet, basename='books')

urlpatterns = [
    path('', include(router.urls))
]
