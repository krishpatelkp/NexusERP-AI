from django.contrib import admin

from .models import (
    Department,
    Designation,
    Employee,
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


# ==========================================================
# EMPLOYEE ADMIN
# ==========================================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Manage company employees.
    """

    list_display = (
        "employee_id",
        "full_name",
        "email",
        "company",
        "department",
        "designation",
        "employment_type",
        "employee_status",
        "is_active",
        "joining_date",
    )

    list_select_related = (
        "company",
        "department",
        "designation",
        "reporting_manager",
        "user_account",
    )

    search_fields = (
        "employee_id",
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "phone",
        "company__company_name",
        "department__department_name",
        "designation__designation_name",
    )

    list_filter = (
        "company",
        "department",
        "designation",
        "employment_type",
        "employee_status",
        "is_active",
    )

    ordering = (
        "company",
        "employee_id",
    )

    readonly_fields = (
        "employee_id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Employee Information",
            {
                "fields": (
                    "employee_id",
                    "company",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "marital_status",
                    "blood_group",
                    "profile_photo",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "email",
                    "phone",
                    "alternate_phone",
                )
            },
        ),
        (
            "Organization",
            {
                "fields": (
                    "department",
                    "designation",
                    "reporting_manager",
                    "user_account",
                    "employment_type",
                    "joining_date",
                    "confirmation_date",
                )
            },
        ),
        (
            "Salary",
            {
                "fields": (
                    "basic_salary",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "employee_status",
                    "is_active",
                    "resignation_date",
                    "termination_date",
                    "retirement_date",
                )
            },
        ),
        (
            "Audit Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )