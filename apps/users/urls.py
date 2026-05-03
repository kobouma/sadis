from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, MeView, ChangePasswordView,
    GoogleSocialLoginView, FacebookSocialLoginView,
)

urlpatterns = [
    path("register/",           RegisterView.as_view(),         name="auth-register"),
    path("login/",              LoginView.as_view(),             name="auth-login"),
    path("logout/",             LogoutView.as_view(),            name="auth-logout"),
    path("token/refresh/",      TokenRefreshView.as_view(),      name="token-refresh"),
    path("me/",                 MeView.as_view(),                name="auth-me"),
    path("me/change-password/", ChangePasswordView.as_view(),    name="auth-change-password"),
    # ── Auth sociale ──────────────────────────────────────────
    path("social/google/",      GoogleSocialLoginView.as_view(), name="social-google"),
    path("social/facebook/",    FacebookSocialLoginView.as_view(),name="social-facebook"),
]