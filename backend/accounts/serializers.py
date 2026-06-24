# React sends JSON  →  Serializer validates it  →  Django saves to DB
# Django fetches DB  →  Serializer converts it  →  React gets JSON

# It's the translator between your API and your database.

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User, Role
from company.models import Company


# ─────────────────────────────────────────
# REGISTER SERIALIZER
# ─────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration.
    Validates email, username, password strength and confirmation.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "phone_number",
            "password",
            "confirm_password",
            "company",
            "role",
        )

    def validate_email(self, value):
        """
        Check that the email is not already registered.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate_username(self, value):
        """
        Check that the username is not already taken.
        Enforce minimum length and allowed characters.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )
        if len(value) < 5:
            raise serializers.ValidationError(
                "Username must be at least 5 characters."
            )
        if not value.replace("_", "").isalnum():
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )
        return value

    def validate(self, attrs):
        """
        Cross-field validation.
        Check passwords match and meet Django's password rules.
        """
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        try:
            validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError(
                {"password": list(e.messages)}
            )

        return attrs

    def create(self, validated_data):
        """
        Remove confirm_password before saving.
        Create user using our custom manager.
        """
        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            username=validated_data["username"],
            phone_number=validated_data.get("phone_number", ""),
            company=validated_data.get("company", None),
            role=validated_data.get("role", None),
        )

        return user


# ─────────────────────────────────────────
# LOGIN SERIALIZER
# ─────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    """
    Handles user login.
    Accepts email and password.
    Does NOT inherit ModelSerializer because
    we are not creating or updating a model here.
    """

    email = serializers.EmailField(required=True)

    password = serializers.CharField(
        required=True,
        write_only=True,
    )


# ─────────────────────────────────────────
# USER PROFILE SERIALIZER
# ─────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Returns current logged-in user's data.
    Used for GET /api/auth/me/
    All fields are read only — this serializer
    never writes to the database.
    """

    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True,
        allow_null=True,
        default=None,
    )

    role_name = serializers.CharField(
        source="role.role_name",
        read_only=True,
        allow_null=True,
        default=None,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "phone_number",
            "company",
            "company_name",
            "role",
            "role_name",
            "is_verified",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


# ─────────────────────────────────────────
# UPDATE PROFILE SERIALIZER
# ─────────────────────────────────────────

class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Allows user to update their own profile.
    Only username and phone_number can be changed here.
    Email and password have separate endpoints.
    """

    class Meta:
        model = User
        fields = (
            "username",
            "phone_number",
        )

    def validate_username(self, value):
        """
        Make sure new username is not taken by another user.
        Allow keeping the same username.
        """
        user = self.context["request"].user

        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )
        if len(value) < 5:
            raise serializers.ValidationError(
                "Username must be at least 5 characters."
            )
        if not value.replace("_", "").isalnum():
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )
        return value


# ─────────────────────────────────────────
# CHANGE PASSWORD SERIALIZER
# ─────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    """
    Allows logged-in user to change their password.
    Requires old password for security.
    """

    old_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    confirm_new_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "Passwords do not match."}
            )

        try:
            validate_password(attrs["new_password"])
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        return attrs


# ─────────────────────────────────────────
# FORGOT PASSWORD SERIALIZER
# ─────────────────────────────────────────

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Accepts email address.
    The view will send a password reset email if the address exists.
    We do not confirm whether the email exists in the response
    for security reasons.
    """

    email = serializers.EmailField(required=True)


# ─────────────────────────────────────────
# RESET PASSWORD SERIALIZER
# ─────────────────────────────────────────

class ResetPasswordSerializer(serializers.Serializer):
    """
    Accepts the reset token and the new password.
    Token comes from the reset email link.
    """

    token = serializers.CharField(required=True)

    new_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    confirm_new_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "Passwords do not match."}
            )

        try:
            validate_password(attrs["new_password"])
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        return attrs