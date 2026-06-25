from django.contrib import admin

from .models import (
    Department,
    Designation,
)


# ==========================================================
# DEPARTMENT ADMIN
# ==========================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Manage company departments.
    """

    list_display = (
        "department_name",
        "department_code",
        "company",
        "is_active",
        "created_at",
    )

    list_select_related = (
        "company",
    )

    search_fields = (
        "department_name",
        "department_code",
        "company__company_name",
        "description",
    )

    list_filter = (
        "company",
        "is_active",
    )

    ordering = (
        "company",
        "department_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Department Information",
            {
                "fields": (
                    "company",
                    "department_name",
                    "department_code",
                    "description",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# ==========================================================
# DESIGNATION ADMIN
# ==========================================================

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    """
    Manage company designations.
    """

    list_display = (
        "designation_name",
        "designation_code",
        "company",
        "is_active",
        "created_at",
    )

    list_select_related = (
        "company",
    )

    search_fields = (
        "designation_name",
        "designation_code",
        "company__company_name",
        "description",
    )

    list_filter = (
        "company",
        "is_active",
    )

    ordering = (
        "company",
        "designation_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Designation Information",
            {
                "fields": (
                    "company",
                    "designation_name",
                    "designation_code",
                    "description",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )