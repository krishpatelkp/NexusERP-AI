from rest_framework import serializers

from employees.models import Employee

from .models import (
    Asset,
    AssetAssignment,
    AssetCategory,
    AssetMaintenance,
    Vendor,
    AssetCondition,
    AssetStatus,
    MaintenanceType,
)


class AssetCategorySerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for AssetCategory.
    """

    class Meta:

        model = AssetCategory

        fields = (
            "id",
            "company",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


class VendorSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for Vendor.
    """

    class Meta:

        model = Vendor

        fields = (
            "id",
            "company",
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "website",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


# ==========================================================
# ASSET SERIALIZER
# ==========================================================

class AssetSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for Asset.

    Includes category and vendor information
    alongside asset details.
    """

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    vendor_name = serializers.SerializerMethodField()

    def get_vendor_name(self, obj):
        if obj.vendor is None:
            return None
        return obj.vendor.name

    class Meta:

        model = Asset

        fields = (
            "id",
            "company",
            "category",
            "category_name",
            "vendor",
            "vendor_name",
            "asset_tag",
            "name",
            "serial_number",
            "brand",
            "model",
            "description",
            "purchase_date",
            "purchase_cost",
            "warranty_expiry",
            "invoice_number",
            "status",
            "condition",
            "location",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields



# ==========================================================
# ASSET ASSIGNMENT SERIALIZER
# ==========================================================

class AssetAssignmentSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for AssetAssignment.

    Includes employee information, asset information,
    snapshot fields, assignment details, and audit
    information.
    """

    employee_id = serializers.CharField(
        source="employee.employee_id",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    asset_name = serializers.CharField(
        source="asset.name",
        read_only=True,
    )

    assigned_by_name = serializers.SerializerMethodField()

    received_by_name = serializers.SerializerMethodField()

    def get_assigned_by_name(self, obj):
        if obj.assigned_by is None:
            return None
        return obj.assigned_by.username

    def get_received_by_name(self, obj):
        if obj.received_by is None:
            return None
        return obj.received_by.username

    class Meta:

        model = AssetAssignment

        fields = (
            "id",
            "company",
            "asset",
            "asset_name",
            "asset_tag_snapshot",
            "employee",
            "employee_id",
            "employee_name",
            "employee_name_snapshot",
            "assigned_date",
            "assigned_condition",
            "assigned_by",
            "assigned_by_name",
            "returned_date",
            "returned_condition",
            "received_by",
            "received_by_name",
            "remarks",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


# ==========================================================
# ASSET MAINTENANCE SERIALIZER
# ==========================================================

class AssetMaintenanceSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for AssetMaintenance.

    Includes asset, vendor,
    maintenance details,
    and audit information.
    """

    asset_name = serializers.CharField(
        source="asset.name",
        read_only=True,
    )

    vendor_name = serializers.SerializerMethodField()

    reported_by_name = serializers.SerializerMethodField()

    def get_vendor_name(self, obj):
        if obj.vendor is None:
            return None
        return obj.vendor.name

    def get_reported_by_name(self, obj):
        if obj.reported_by is None:
            return None
        return obj.reported_by.username

    class Meta:

        model = AssetMaintenance

        fields = (
            "id",
            "asset",
            "asset_name",
            "asset_tag_snapshot",
            "vendor",
            "vendor_name",
            "maintenance_type",
            "status",
            "description",
            "scheduled_date",
            "completed_date",
            "cost",
            "outcome_notes",
            "reported_by",
            "reported_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


# ==========================================================
# CREATE ASSET SERIALIZER
# ==========================================================

class CreateAssetSerializer(
    serializers.Serializer,
):
    """
    Accepts input for creating an asset.

    Business validation is handled by
    InventoryService.
    """

    category = serializers.PrimaryKeyRelatedField(
        queryset=AssetCategory.objects.all(),
    )

    asset_tag = serializers.CharField(
        max_length=50,
    )

    name = serializers.CharField(
        max_length=150,
    )

    vendor = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(),
        required=False,
        allow_null=True,
    )

    serial_number = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    brand = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    model = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    purchase_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    purchase_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    warranty_expiry = serializers.DateField(
        required=False,
        allow_null=True,
    )

    invoice_number = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    condition = serializers.ChoiceField(
        choices=AssetCondition.choices,
        default=AssetCondition.NEW,
    )

    location = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# ASSIGN ASSET SERIALIZER
# ==========================================================

class AssignAssetSerializer(
    serializers.Serializer,
):
    """
    Accepts input for assigning
    an asset to an employee.
    """

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
    )

    assigned_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    assigned_condition = serializers.ChoiceField(
        choices=AssetCondition.choices,
        default=AssetCondition.GOOD,
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# RETURN ASSET SERIALIZER
# ==========================================================

class ReturnAssetSerializer(
    serializers.Serializer,
):
    """
    Accepts input for returning
    an assigned asset.
    """

    returned_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    returned_condition = serializers.ChoiceField(
        choices=AssetCondition.choices,
        required=False,
        allow_null=True,
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# SCHEDULE MAINTENANCE SERIALIZER
# ==========================================================

class ScheduleMaintenanceSerializer(
    serializers.Serializer,
):
    """
    Accepts input for scheduling
    asset maintenance.
    """

    maintenance_type = serializers.ChoiceField(
        choices=MaintenanceType.choices,
    )

    description = serializers.CharField()

    scheduled_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    vendor = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(),
        required=False,
        allow_null=True,
    )

    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    outcome_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# COMPLETE MAINTENANCE SERIALIZER
# ==========================================================

class CompleteMaintenanceSerializer(
    serializers.Serializer,
):
    """
    Accepts input for completing
    maintenance.
    """

    completed_date = serializers.DateField(
        required=False,
        allow_null=True,
    )

    asset_status = serializers.ChoiceField(
        choices=AssetStatus.choices,
        default=AssetStatus.AVAILABLE,
    )

    asset_condition = serializers.ChoiceField(
        choices=AssetCondition.choices,
        required=False,
        allow_null=True,
    )

    outcome_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# RETIRE ASSET SERIALIZER
# ==========================================================

class RetireAssetSerializer(
    serializers.Serializer,
):
    """
    Accepts input for retiring
    an asset.
    """

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )