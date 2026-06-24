from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import authenticate

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


# ─────────────────────────────────────────
# HELPER FUNCTION
# ─────────────────────────────────────────

def get_tokens_for_user(user):
    """
    Generate JWT access and refresh tokens for a user.
    Called after successful register or login.
    """
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# ─────────────────────────────────────────
# REGISTER VIEW
# ─────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Creates a new user account.
    No authentication required.
    """

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response(
                {
                    "message": "Account created successfully.",
                    "user": UserProfileSerializer(user).data,
                    "tokens": tokens,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ─────────────────────────────────────────
# LOGIN VIEW
# ─────────────────────────────────────────

class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticates user and returns JWT tokens.
    No authentication required.
    """

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            user = authenticate(
                request=request,
                username=email,
                password=password,
            )

            if user is None:
                return Response(
                    {"error": "Invalid email or password."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not user.is_active:
                return Response(
                    {"error": "Your account has been deactivated."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            tokens = get_tokens_for_user(user)

            return Response(
                {
                    "message": "Login successful.",
                    "user": UserProfileSerializer(user).data,
                    "tokens": tokens,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ─────────────────────────────────────────
# LOGOUT VIEW
# ─────────────────────────────────────────

class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklists the refresh token so it cannot be used again.
    User must be authenticated to logout.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ─────────────────────────────────────────
# CURRENT USER VIEW
# ─────────────────────────────────────────

class MeView(APIView):
    """
    GET /api/auth/me/
    Returns the currently logged-in user's profile.
    Authentication required.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────
# UPDATE PROFILE VIEW
# ─────────────────────────────────────────

class UpdateProfileView(APIView):
    """
    PUT /api/auth/me/update/
    Allows logged-in user to update username and phone number.
    Authentication required.
    """

    permission_classes = [IsAuthenticated]

    def put(self, request):

        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Profile updated successfully.",
                    "user": UserProfileSerializer(request.user).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ─────────────────────────────────────────
# CHANGE PASSWORD VIEW
# ─────────────────────────────────────────

class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    Allows logged-in user to change their password.
    Requires old password for verification.
    Authentication required.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():

            user = request.user

            if not user.check_password(
                serializer.validated_data["old_password"]
            ):
                return Response(
                    {"error": "Old password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(
                serializer.validated_data["new_password"]
            )
            user.save()

            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ─────────────────────────────────────────
# FORGOT PASSWORD VIEW
# ─────────────────────────────────────────

class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/
    Accepts an email address.
    In production this would send a reset email.
    For now we return the token directly so you can test it.
    No authentication required.
    """

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data["email"]

            try:
                user = User.objects.get(email=email)
                refresh = RefreshToken.for_user(user)
                reset_token = str(refresh.access_token)

                # TODO: Send email with reset_token in production
                # For now return it directly for testing

                return Response(
                    {
                        "message": "Password reset token generated.",
                        "reset_token": reset_token,
                    },
                    status=status.HTTP_200_OK,
                )

            except User.DoesNotExist:
                # Always return 200 even if email not found
                # This prevents attackers from knowing which
                # emails are registered in your system
                return Response(
                    {"message": "If this email exists, a reset link has been sent."},
                    status=status.HTTP_200_OK,
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


# ─────────────────────────────────────────
# RESET PASSWORD VIEW
# ─────────────────────────────────────────

class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/
    Accepts reset token and new password.
    Verifies the token and updates the password.
    No authentication required.
    """

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():

            token_string = serializer.validated_data["token"]

            try:
                from rest_framework_simplejwt.tokens import AccessToken

                token = AccessToken(token_string)
                user_id = token["user_id"]
                user = User.objects.get(id=user_id)

                user.set_password(
                    serializer.validated_data["new_password"]
                )
                user.save()

                return Response(
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )

            except Exception:
                return Response(
                    {"error": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
