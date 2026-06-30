from django.contrib import admin

from .models import Payment


# ==========================================================
# PAYMENT ADMIN
# ==========================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "payment_number",
        "employee",
        "amount",
        "payment_method",
        "status",
        "payment_date",
        "processed_by",
    )

    list_filter = (
        "company",
        "status",
        "payment_method",
        "payment_date",
    )

    search_fields = (
        "payment_number",
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "transaction_id",
        "bank_reference_number",
    )

    ordering = (
        "-created_at",
    )

    autocomplete_fields = (
        "company",
        "payslip",
        "employee",
        "processed_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "processed_at",
    )