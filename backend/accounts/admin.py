from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import User, Role, Permission, RolePermission
from .forms import CustomUserCreationForm, CustomUserChangeForm


# ─────────────────────────────────────────
# PERMISSION ADMIN
# ─────────────────────────────────────────

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Manage all permissions available in the ERP.
    """

    list_display = (
        "permission_name",
        "permission_code",
        "is_active",
        "created_at",
    )

    search_fields = (
        "permission_name",
        "permission_code",
        "description",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "permission_code",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Permission Information", {
            "fields": (
                "permission_name",
                "permission_code",
                "description",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


# ─────────────────────────────────────────
# ROLE PERMISSION INLINE
# ─────────────────────────────────────────

class RolePermissionInline(admin.TabularInline):
    """
    Shows permissions assigned to a role
    directly inside the Role admin page.
    This way you can assign permissions to a role
    without leaving the Role page.
    """

    model = RolePermission
    extra = 1
    show_change_link = True

    fields = (
        "permission",
        "is_active",
    )

    autocomplete_fields = (
        "permission",
    )


# ─────────────────────────────────────────
# ROLE ADMIN
# ─────────────────────────────────────────

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Manage roles and their assigned permissions.
    """

    list_select_related = (
        "company",
    )

    list_display = (
        "role_name",
        "role_code",
        "company",
        "is_active",
        "permission_count",
    )

    search_fields = (
        "role_name",
        "role_code",
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

    inlines = [
        RolePermissionInline,
    ]

    fieldsets = (
        ("Role Information", {
            "fields": (
                "company",
                "role_name",
                "role_code",
                "description",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


    @admin.display(description="Permissions")
    def permission_count(self, obj):
        return obj.role_permissions.filter(
            is_active=True
            ).count()


# ─────────────────────────────────────────
# ROLE PERMISSION ADMIN
# ─────────────────────────────────────────

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """
    Direct view of all role-permission mappings.
    Useful for auditing which role has which permission.
    """
    
    list_select_related = (
        "role",
        "permission",
    )

    list_display = (
        "role",
        "permission",
        "is_active",
        "created_at",
    )

    search_fields = (
        "role__role_name",
        "role__company__company_name",
        "permission__permission_name",
        "permission__permission_code",
    )

    list_filter = (
        "is_active",
        "role__company",
    )

    ordering = (
        "role",
        "permission",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "role",
        "permission",
    )


# ─────────────────────────────────────────
# USER ADMIN
# ─────────────────────────────────────────

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

    list_select_related = (
        "company",
        "role",
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