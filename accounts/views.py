from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.serializers import MyTokenObtainPairSerializer, RegistrationSerializer
from accounts.throttles import LoginThrottle, RefreshThrottle, RegistrationThrottle


@permission_classes(
    [
        AllowAny,
    ]
)
class RegistrationView(GenericAPIView):
    authentication_classes = []
    serializer_class = RegistrationSerializer
    throttle_classes = [RegistrationThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]
    serializer_class = MyTokenObtainPairSerializer


class LimitedTokenRefreshView(TokenRefreshView):
    throttle_classes = [RefreshThrottle]
