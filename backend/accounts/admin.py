from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import User, Role
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        "role_name",
        "company",
        "is_active",
    )

    search_fields = (
        "role_name",
        "company__company_name",
    )

    list_filter = (
        "company",
        "is_active",
    )

    ordering = (
        "company",
        "role_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        "email",
        "username",
        "company",
        "role",
        "is_active",
        "is_staff",
        "is_verified",
    )

    search_fields = (
        "email",
        "username",
        "company__company_name",
        "role__role_name",
    )

    list_filter = (
        "company",
        "role",
        "is_active",
        "is_staff",
        "is_verified",
        "is_superuser",
    )

    ordering = (
        "email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
    )

    fieldsets = (

        ("Login Information", {
            "fields": (
                "email",
                "password",
            )
        }),

        ("Personal Information", {
            "fields": (
                "username",
                "phone_number",
            )
        }),

        ("Organization", {
            "fields": (
                "company",
                "role",
            )
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "is_verified",
                "groups",
                "user_permissions",
            )
        }),

        ("Important Dates", {
            "fields": (
                "last_login",
                "created_at",
                "updated_at",
            )
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "phone_number",
                    "company",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_verified",
                ),
            },
        ),
    )