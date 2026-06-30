from django.contrib import admin

# Register your models here.
from .models import (
    Asset,
    AssetAssignment,
    AssetCategory,
    AssetMaintenance,
    Vendor,
)

@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "description",
        "company__company_name",
    )

    ordering = (
        "company",
        "name",
    )

    autocomplete_fields = (
        "company",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "email",
        "phone",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "company__company_name",
    )

    ordering = (
        "company",
        "name",
    )

    autocomplete_fields = (
        "company",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):

    list_display = (
        "asset_tag",
        "name",
        "category",
        "company",
        "status",
        "condition",
        "is_active",
    )

    list_filter = (
        "company",
        "category",
        "status",
        "condition",
        "is_active",
    )

    search_fields = (
        "asset_tag",
        "name",
        "serial_number",
        "invoice_number",
        "company__company_name",
        "vendor__name",
    )

    ordering = (
        "company",
        "asset_tag",
    )

    autocomplete_fields = (
        "company",
        "category",
        "vendor",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "asset",
        "employee",
        "assigned_date",
        "returned_date",
    )

    list_filter = (
        "company",
        "assigned_date",
        "returned_date",
    )

    search_fields = (
        "asset__asset_tag",
        "asset__name",
        "employee__employee_id",
        "employee__full_name",
        "asset_tag_snapshot",
        "employee_name_snapshot",
    )

    ordering = (
        "-assigned_date",
    )

    autocomplete_fields = (
        "company",
        "asset",
        "employee",
        "assigned_by",
    )

    readonly_fields = (
        "asset_tag_snapshot",
        "employee_name_snapshot",
        "created_at",
        "updated_at",
    )


@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):

    list_display = (
        "asset",
        "maintenance_type",
        "status",
        "scheduled_date",
        "completed_date",
        "cost",
    )

    list_filter = (
        "company",
        "maintenance_type",
        "status",
        "scheduled_date",
    )

    search_fields = (
        "asset__asset_tag",
        "asset__name",
        "asset_tag_snapshot",
        "description",
        "outcome_notes",
        "vendor__name",
    )

    ordering = (
        "-scheduled_date",
    )

    autocomplete_fields = (
        "company",
        "asset",
        "vendor",
        "reported_by",
    )

    readonly_fields = (
        "asset_tag_snapshot",
        "created_at",
        "updated_at",
    )