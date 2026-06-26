from django.contrib import admin

from .models import (
    Department,
    Designation,
    Employee,
    EmployeeAddress,
    EmergencyContact,
    EmployeeBankDetail,
    EmployeeDocument,
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


# ==========================================================
# EMPLOYEE ADDRESS ADMIN
# ==========================================================

@admin.register(EmployeeAddress)
class EmployeeAddressAdmin(admin.ModelAdmin):
    """
    Manage employee addresses.
    """

    list_display = (
        "employee",
        "address_type",
        "city",
        "state",
        "country",
        "postal_code",
        "is_active",
        "created_at",
    )

    list_select_related = (
        "employee",
    )

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "city",
        "state",
        "country",
        "postal_code",
        "address_line_1",
    )

    list_filter = (
        "address_type",
        "country",
        "state",
        "is_active",
    )

    ordering = (
        "employee",
        "address_type",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Employee",
            {
                "fields": (
                    "employee",
                    "address_type",
                )
            },
        ),
        (
            "Address Details",
            {
                "fields": (
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "state",
                    "country",
                    "postal_code",
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
# EMERGENCY CONTACT ADMIN
# ==========================================================

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    """
    Manage employee emergency contacts.
    """

    list_display = (
        "employee",
        "contact_name",
        "relationship",
        "phone",
        "is_primary",
        "is_active",
        "created_at",
    )

    list_select_related = (
        "employee",
    )

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "contact_name",
        "phone",
        "alternate_phone",
        "email",
    )

    list_filter = (
        "relationship",
        "is_primary",
        "is_active",
    )

    ordering = (
        "employee",
        "-is_primary",
        "contact_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Employee Information",
            {
                "fields": (
                    "employee",
                )
            },
        ),
        (
            "Emergency Contact",
            {
                "fields": (
                    "contact_name",
                    "relationship",
                    "phone",
                    "alternate_phone",
                    "email",
                    "address",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_primary",
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
# EMPLOYEE BANK DETAIL ADMIN
# ==========================================================

@admin.register(EmployeeBankDetail)
class EmployeeBankDetailAdmin(admin.ModelAdmin):
    """
    Manage employee bank details.
    """

    list_display = (
        "employee",
        "bank_name",
        "account_holder_name",
        "account_number",
        "ifsc_code",
        "account_type",
        "is_primary",
        "is_active",
        "created_at",
    )

    list_select_related = (
        "employee",
    )

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "bank_name",
        "account_holder_name",
        "account_number",
        "ifsc_code",
        "upi_id",
    )

    list_filter = (
        "account_type",
        "is_primary",
        "is_active",
    )

    ordering = (
        "employee",
        "-is_primary",
        "bank_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Employee Information",
            {
                "fields": (
                    "employee",
                )
            },
        ),
        (
            "Bank Information",
            {
                "fields": (
                    "bank_name",
                    "branch_name",
                    "account_holder_name",
                    "account_number",
                    "ifsc_code",
                    "account_type",
                    "upi_id",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_primary",
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
# EMPLOYEE DOCUMENT ADMIN
# ==========================================================

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    """
    Manage employee documents.
    """

    list_display = (
        "employee",
        "document_name",
        "document_type",
        "is_verified",
        "is_active",
        "created_at",
    )

    list_select_related = (
        "employee",
    )

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "document_name",
        "description",
    )

    list_filter = (
        "document_type",
        "is_verified",
        "is_active",
    )

    ordering = (
        "employee",
        "document_type",
        "document_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Employee Information",
            {
                "fields": (
                    "employee",
                )
            },
        ),
        (
            "Document Information",
            {
                "fields": (
                    "document_type",
                    "document_name",
                    "file",
                    "description",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_verified",
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