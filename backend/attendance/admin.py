from django.contrib import admin

from .models import (
    Holiday,
    Attendance,
)


# ==========================================================
# HOLIDAY ADMIN
# ==========================================================

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Holiday model.
    """

    list_display = (
        "name",
        "company",
        "date",
        "holiday_type",
        "is_optional",
        "is_recurring",
        "is_active",
    )

    list_select_related = (
        "company",
    )

    search_fields = (
        "name",
        "company__company_name",
        "description",
    )

    list_filter = (
        "company",
        "holiday_type",
        "is_optional",
        "is_recurring",
        "is_active",
    )

    ordering = (
        "date",
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Holiday Information",
            {
                "fields": (
                    "company",
                    "name",
                    "date",
                    "holiday_type",
                    "description",
                )
            },
        ),
        (
            "Configuration",
            {
                "fields": (
                    "is_optional",
                    "is_recurring",
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

    def get_readonly_fields(
        self,
        request,
        obj=None,
    ):
        """
        Prevent changing the company after creation.
        """

        readonly = list(self.readonly_fields)

        if obj:

            readonly.append(
                "company",
            )

        return readonly
    

# ==========================================================
# ATTENDANCE ADMIN
# ==========================================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Attendance model.
    """

    list_display = (
        "employee",
        "date",
        "status",
        "check_in",
        "check_out",
        "working_minutes",
        "overtime_minutes",
        "is_active",
    )

    list_select_related = (
        "employee",
        "shift",
    )

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "employee__email",
    )

    list_filter = (
        "status",
        "shift",
        "date",
        "is_active",
        "employee__company",
    )

    ordering = (
        "-date",
        "employee",
    )

    readonly_fields = (
        "scheduled_start_time",
        "scheduled_end_time",
        "scheduled_grace_minutes",
        "working_minutes",
        "late_minutes",
        "early_exit_minutes",
        "overtime_minutes",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Attendance Information",
            {
                "fields": (
                    "employee",
                    "shift",
                    "date",
                    "status",
                )
            },
        ),
        (
            "Scheduled Time",
            {
                "fields": (
                    "scheduled_start_time",
                    "scheduled_end_time",
                    "scheduled_grace_minutes",
                )
            },
        ),
        (
            "Attendance Time",
            {
                "fields": (
                    "check_in",
                    "check_out",
                )
            },
        ),
        (
            "Calculated Values",
            {
                "fields": (
                    "working_minutes",
                    "late_minutes",
                    "early_exit_minutes",
                    "overtime_minutes",
                )
            },
        ),
        (
            "Remarks",
            {
                "fields": (
                    "remarks",
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

    def get_readonly_fields(
        self,
        request,
        obj=None,
):
        """
        Prevent changing historical attendance information
        after the record has been created.
        """

        readonly = list(self.readonly_fields)

        if obj:
            readonly.extend(
            [
                "employee",
                "shift",
            ]
        )

        return readonly