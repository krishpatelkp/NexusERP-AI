from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Form used in Django Admin to create a new user.
    """

    class Meta:
        model = User

        fields = (
            "email",
            "username",
            "phone_number",
            "company",
            "role",
            "is_active",
            "is_staff",
            "is_verified",
        )

class CustomUserChangeForm(UserChangeForm):
    """
    Form used in Django Admin to edit an existing user.
    """

    class Meta:
        model = User

        fields = (
            "email",
            "username",
            "phone_number",
            "company",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_verified",
            "groups",
            "user_permissions",
        )