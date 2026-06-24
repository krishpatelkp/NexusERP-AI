from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    UpdateProfileView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)

urlpatterns = [

    # ─────────────────────────────────────────
    # REGISTER
    # ─────────────────────────────────────────
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    # ─────────────────────────────────────────
    # LOGIN
    # ─────────────────────────────────────────
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    # ─────────────────────────────────────────
    # TOKEN REFRESH
    # ─────────────────────────────────────────
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # ─────────────────────────────────────────
    # LOGOUT
    # ─────────────────────────────────────────
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    # ─────────────────────────────────────────
    # CURRENT USER
    # ─────────────────────────────────────────
    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),

    # ─────────────────────────────────────────
    # UPDATE PROFILE
    # ─────────────────────────────────────────
    path(
        "me/update/",
        UpdateProfileView.as_view(),
        name="me_update",
    ),

    # ─────────────────────────────────────────
    # CHANGE PASSWORD
    # ─────────────────────────────────────────
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),

    # ─────────────────────────────────────────
    # FORGOT PASSWORD
    # ─────────────────────────────────────────
    path(
        "forgot-password/",
        ForgotPasswordView.as_view(),
        name="forgot_password",
    ),

    # ─────────────────────────────────────────
    # RESET PASSWORD
    # ─────────────────────────────────────────
    path(
        "reset-password/",
        ResetPasswordView.as_view(),
        name="reset_password",
    ),

]