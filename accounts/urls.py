from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from . import browser_views as browser
from .views import MyTokenObtainPairView, RegistrationView

urlpatterns = [
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
    path("register/", RegistrationView.as_view(), name="register"),
]


urlpatterns += [
    path("auth/csrf/", browser.CSRFView.as_view()),
    path("auth/register/", browser.BrowserRegisterView.as_view()),
    path("auth/login/", browser.BrowserLoginView.as_view()),
    path("auth/refresh/", browser.BrowserRefreshView.as_view()),
    path("auth/logout/", browser.BrowserLogoutView.as_view()),
    path("auth/me/", browser.ProfileView.as_view()),
    path("auth/password/change/", browser.ChangePasswordView.as_view()),
    path("auth/password/reset/", browser.PasswordResetRequestView.as_view()),
    path("auth/password/reset/confirm/", browser.PasswordResetConfirmView.as_view()),
    path("auth/email/verify/", browser.VerifyEmailView.as_view()),
    path("auth/email/resend/", browser.ResendVerificationView.as_view()),
    path("auth/sessions/revoke/", browser.LogoutAllView.as_view()),
    path("auth/account/", browser.DeleteAccountView.as_view()),
]
