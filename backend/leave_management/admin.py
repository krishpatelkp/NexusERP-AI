from django.contrib import admin

from .models import (
    LeaveType,
    LeaveBalance,
    LeaveRequest,
)

# ==========================================================
# LEAVE TYPE ADMIN
# ==========================================================

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaveType.
    """

    list_display = (
        "leave_name",
        "leave_code",
        "company",
        "max_days_per_year",
        "max_consecutive_days",
        "is_paid",
        "carry_forward",
        "requires_approval",
        "is_active",
    )

    list_filter = (
        "company",
        "is_paid",
        "carry_forward",
        "requires_approval",
        "is_active",
    )

    search_fields = (
        "leave_name",
        "leave_code",
        "company__company_name",
    )

    ordering = (
        "company",
        "leave_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 25

    list_select_related = (
        "company",
    )

    fieldsets = (

        (
            "Basic Information",
            {
                "fields": (
                    "company",
                    "leave_name",
                    "leave_code",
                    "description",
                )
            },
        ),

        (
            "Leave Policy",
            {
                "fields": (
                    "max_days_per_year",
                    "max_consecutive_days",
                    "is_paid",
                    "carry_forward",
                    "requires_approval",
                    "is_active",
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
# LEAVE BALANCE ADMIN
# ==========================================================

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaveBalance.
    """

    list_display = (
        "employee",
        "leave_type",
        "company",
        "year",
        "allocated_days",
        "used_days",
        "remaining_days",
    )

    list_filter = (
        "company",
        "leave_type",
        "year",
    )

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "leave_type__leave_name",
        "company__company_name",
    )

    ordering = (
        "company",
        "employee",
        "-year",
    )

    readonly_fields = (
        "remaining_days",
        "created_at",
        "updated_at",
    )

    list_per_page = 25

    list_select_related = (
        "company",
        "employee",
        "leave_type",
    )

    autocomplete_fields = (
        "company",
        "employee",
        "leave_type",
    )

    save_on_top = True

    fieldsets = (

        (
            "Employee Information",
            {
                "fields": (
                    "company",
                    "employee",
                    "leave_type",
                    "year",
                ),
            },
        ),

        (
            "Leave Balance",
            {
                "fields": (
                    "allocated_days",
                    "used_days",
                    "remaining_days",
                ),
            },
        ),

        (
            "Audit Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),

    )


# ==========================================================
# LEAVE REQUEST ADMIN
# ==========================================================

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for LeaveRequest.
    """

    list_display = (
        "employee",
        "leave_type_snapshot",
        "company",
        "start_date",
        "end_date",
        "total_days",
        "leave_status",
        "approval_status",
        "approved_by",
    )

    list_filter = (
        "company",
        "leave_status",
        "approval_status",
        "leave_source",
        "is_half_day",
        "start_date",
        "end_date",
        "request_date",
    )

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "leave_type_snapshot",
        "reason",
        "remarks",
        "company__company_name",
    )

    ordering = (
        "-start_date",
        "-created_at",
    )

    readonly_fields = (
        "leave_type_snapshot",
        "request_date",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "company",
        "employee",
        "leave_type",
        "approved_by",
        "last_modified_by",
    )

    list_per_page = 25

    date_hierarchy = "start_date"

    save_on_top = True

    fieldsets = (

        (
            "Employee Information",
            {
                "fields": (
                    "company",
                    "employee",
                    "leave_type",
                    "leave_type_snapshot",
                ),
            },
        ),

        (
            "Leave Details",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "total_days",
                    "is_half_day",
                    "reason",
                    "remarks",
                ),
            },
        ),

        (
            "Approval Workflow",
            {
                "fields": (
                    "leave_status",
                    "approval_status",
                    "approved_by",
                    "approved_at",
                    "approval_reason",
                ),
            },
        ),

        (
            "AI & Audit",
            {
                "fields": (
                    "leave_source",
                    "leave_modified",
                    "last_modified_by",
                    "request_date",
                    "created_at",
                    "updated_at",
                ),
            },
        ),

    )