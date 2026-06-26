from django.contrib import admin

from .models import Holiday


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