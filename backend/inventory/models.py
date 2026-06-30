from django.core.exceptions import ValidationError
from django.db import models

from company.models import Company


# ==========================================================
# ASSET CATEGORY
# ==========================================================

class AssetCategory(models.Model):
    """
    Represents a category of company assets.

    Examples:
        Laptop
        Desktop
        Mobile
        Monitor
        Printer
        Furniture
        Network Device
        Accessory

    Every asset belongs to exactly one category.

    Design:
        This model only answers one question:
        "What type of asset is this?"

        No code field is used here because category
        names (e.g. "Laptop") are already stable,
        human-readable identifiers. Unlike Department
        or Designation, categories do not map to
        external systems that require short codes.

    Immutability:
        Categories are never deleted.
        Use is_active=False instead.
        This preserves history for assets that
        reference an old or discontinued category.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="asset_categories",
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "company",
            "name",
        ]

        verbose_name = "Asset Category"

        verbose_name_plural = "Asset Categories"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "company",
                    "name",
                ],
                name="unique_asset_category_per_company",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.name is not None:
            self.name = self.name.strip()

        if self.description is not None:
            self.description = self.description.strip()

        if not self.name:
            raise ValidationError(
                {
                    "name":
                    "Category name is required."
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.name:
            self.name = self.name.strip()

        if self.description:
            self.description = self.description.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.company.company_name}"
            f" - "
            f"{self.name}"
        )
    
# ==========================================================
# VENDOR
# ==========================================================

class Vendor(models.Model):
    """
    Represents a supplier/vendor that the company
    purchases assets from.

    Examples:
        Dell
        HP
        Lenovo
        Apple
        Local IT Supplier

    Used for:
        - Tracking where an asset was purchased
        - Warranty and support contact information
        - Future AI analysis of vendor quality
          (e.g. which vendor's assets fail more often)

    Immutability:
        Vendors are never deleted.
        Use is_active=False instead.
        Assets reference vendors historically —
        deleting a vendor would break purchase records.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="vendors",
    )

    name = models.CharField(
        max_length=150,
    )

    contact_person = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    email = models.EmailField(
        blank=True,
        default="",
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        default="",
    )

    address = models.TextField(
        blank=True,
        default="",
    )

    website = models.URLField(
        blank=True,
        default="",
    )

    notes = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Internal notes about this vendor. "
            "e.g. payment terms, reliability, "
            "warranty support quality."
        ),
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "company",
            "name",
        ]

        verbose_name = "Vendor"

        verbose_name_plural = "Vendors"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "company",
                    "name",
                ],
                name="unique_vendor_name_per_company",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.name is not None:
            self.name = self.name.strip()

        if self.contact_person is not None:
            self.contact_person = (
                self.contact_person.strip()
            )

        if self.address is not None:
            self.address = self.address.strip()

        if self.notes is not None:
            self.notes = self.notes.strip()

        if not self.name:
            raise ValidationError(
                {
                    "name":
                    "Vendor name is required."
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.name:
            self.name = self.name.strip()

        if self.contact_person:
            self.contact_person = (
                self.contact_person.strip()
            )

        if self.address:
            self.address = self.address.strip()

        if self.notes:
            self.notes = self.notes.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.company.company_name}"
            f" - "
            f"{self.name}"
        )
    

# ==========================================================
# ASSET STATUS
# ==========================================================

class AssetStatus(models.TextChoices):
    AVAILABLE   = "Available",   "Available"
    ASSIGNED    = "Assigned",    "Assigned"
    MAINTENANCE = "Maintenance", "Maintenance"
    LOST        = "Lost",        "Lost"
    DAMAGED     = "Damaged",     "Damaged"
    RETIRED     = "Retired",     "Retired"


# ==========================================================
# ASSET CONDITION
# ==========================================================

class AssetCondition(models.TextChoices):
    NEW      = "New",      "New"
    GOOD     = "Good",     "Good"
    FAIR     = "Fair",     "Fair"
    POOR     = "Poor",     "Poor"


# ==========================================================
# ASSET
# ==========================================================

class Asset(models.Model):
    """
    Represents a single physical company asset.

    Examples:
        Laptop - Dell Latitude 5420 - SN: ABC123
        Office Chair - Ergonomic - TAG: CHR-045

    Design:
        Each Asset is a distinct, trackable item —
        not a product type. Two identical laptops
        purchased together are two separate Asset
        records, each with its own asset_tag and
        serial_number.

    Status Lifecycle:
        Available   → In stock, not assigned
        Assigned    → Currently held by an employee
        Maintenance → Sent for repair/service
        Lost        → Reported lost
        Damaged     → Reported damaged, unusable
        Retired     → End of life, no longer in use

    Immutability:
        Assets are never deleted, even when Lost,
        Damaged, or Retired. Historical assignment
        and maintenance records must always be
        traceable back to the asset.

    Integration:
        AssetAssignment tracks who holds this asset
        and when, over time.
        AssetMaintenance tracks repair/service history.

    AI Readiness:
        purchase_date, purchase_cost, warranty_expiry,
        and status changes over time enable AI to
        analyze asset lifespan, depreciation, and
        replacement planning.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="assets",
    )

    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.PROTECT,
        related_name="assets",
        help_text=(
            "Cannot delete a category that "
            "has assets assigned to it."
        ),
    )

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
        help_text="Vendor this asset was purchased from.",
    )

    # ──────────────────────────────────────
    # IDENTIFICATION
    # ──────────────────────────────────────

    asset_tag = models.CharField(
        max_length=50,
        help_text=(
            "Internal company asset tag. "
            "e.g. LAP-0001, CHR-0045"
        ),
    )

    name = models.CharField(
        max_length=150,
        help_text="e.g. Dell Latitude 5420",
    )

    serial_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Manufacturer serial number, if applicable.",
    )

    brand = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    model = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    # ──────────────────────────────────────
    # PURCHASE INFORMATION
    # ──────────────────────────────────────

    purchase_date = models.DateField(
        null=True,
        blank=True,
    )

    purchase_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    warranty_expiry = models.DateField(
        null=True,
        blank=True,
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    # ──────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.AVAILABLE,
    )

    condition = models.CharField(
        max_length=20,
        choices=AssetCondition.choices,
        default=AssetCondition.NEW,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text=(
            "Physical location when not assigned. "
            "e.g. IT Store Room, Floor 3 Storage"
        ),
    )

    notes = models.TextField(
        blank=True,
        default="",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "company",
            "category",
            "asset_tag",
        ]

        verbose_name = "Asset"

        verbose_name_plural = "Assets"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "company",
                    "asset_tag",
                ],
                name="unique_asset_tag_per_company",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["category"],
            ),

            models.Index(
                fields=["vendor"],
            ),

            models.Index(
                fields=["status"],
            ),

            models.Index(
                fields=["asset_tag"],
            ),

            models.Index(
                fields=["serial_number"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.asset_tag is not None:
            self.asset_tag = self.asset_tag.strip().upper()

        if self.name is not None:
            self.name = self.name.strip()

        if self.serial_number is not None:
            self.serial_number = self.serial_number.strip()

        if self.brand is not None:
            self.brand = self.brand.strip()

        if self.model is not None:
            self.model = self.model.strip()

        if self.description is not None:
            self.description = self.description.strip()

        if self.location is not None:
            self.location = self.location.strip()

        if self.notes is not None:
            self.notes = self.notes.strip()

        if not self.asset_tag:
            raise ValidationError(
                {
                    "asset_tag":
                    "Asset tag is required."
                }
            )

        if not self.name:
            raise ValidationError(
                {
                    "name":
                    "Asset name is required."
                }
            )

        if (
            self.purchase_cost is not None
            and self.purchase_cost < 0
        ):
            raise ValidationError(
                {
                    "purchase_cost":
                    "Purchase cost cannot be negative."
                }
            )

        # Category must belong to same company
        if (
            self.category
            and self.company
            and self.category.company != self.company
        ):
            raise ValidationError(
                {
                    "category":
                    (
                        "Asset category does not "
                        "belong to this company."
                    )
                }
            )

        # Vendor must belong to same company
        if (
            self.vendor
            and self.company
            and self.vendor.company != self.company
        ):
            raise ValidationError(
                {
                    "vendor":
                    (
                        "Vendor does not belong "
                        "to this company."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.asset_tag:
            self.asset_tag = self.asset_tag.strip().upper()

        if self.name:
            self.name = self.name.strip()

        if self.serial_number:
            self.serial_number = self.serial_number.strip()

        if self.brand:
            self.brand = self.brand.strip()

        if self.model:
            self.model = self.model.strip()

        if self.description:
            self.description = self.description.strip()

        if self.location:
            self.location = self.location.strip()

        if self.notes:
            self.notes = self.notes.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def is_available(self):
        """
        Returns True if this asset can be assigned.
        """
        return self.status == AssetStatus.AVAILABLE

    @property
    def is_under_warranty(self):
        """
        Returns True if this asset is still
        within its warranty period.
        """
        if not self.warranty_expiry:
            return False

        from django.utils import timezone
        return self.warranty_expiry >= timezone.localdate()

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.asset_tag}"
            f" - "
            f"{self.name}"
        )
    

# ==========================================================
# ASSET ASSIGNMENT
# ==========================================================

class AssetAssignment(models.Model):
    """
    Represents one period during which an asset
    was held by a specific employee.

    This is a history table, not a live status field.
    Every assignment and return creates a new record
    or closes an existing one — nothing is ever
    overwritten or deleted.

    Example lifecycle for one laptop:

        Assignment 1
            Employee: Rahul
            Assigned: 01-Jan-2026
            Returned: 10-Jun-2026

        Assignment 2
            Employee: Amit
            Assigned: 12-Jun-2026
            Returned: null (currently holding)

    Design rule:
        An asset can have at most ONE assignment
        with returned_date = null at any given time.
        This represents "who currently holds it".

    Why not edit the existing assignment when
    reassigning to someone else?
        Because that would destroy the fact that
        Rahul ever held this laptop. Audits, AI
        analytics, and accountability all depend
        on this history being permanent.

    What happens when an employee leaves?
        The assignment is NOT deleted. It should be
        closed (returned_date set) as part of the
        offboarding process. The service layer will
        enforce this — an employee with status
        Resigned/Terminated cannot hold an open
        assignment.

    AI Readiness:
        This table enables questions like:
        - Average time an asset stays with one employee
        - Employees holding assets after resignation
        - Asset turnover rate per department
        - Which employees lose/damage assets most often
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="asset_assignments",
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="assignments",
        help_text=(
            "Cannot delete an asset that has "
            "assignment history."
        ),
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="asset_assignments",
        help_text=(
            "Cannot delete an employee that has "
            "asset assignment history."
        ),
    )

    # ──────────────────────────────────────
    # SNAPSHOT FIELDS
    # ──────────────────────────────────────

    asset_tag_snapshot = models.CharField(
        max_length=50,
        help_text=(
            "Snapshot of the asset tag at "
            "assignment time."
        ),
    )

    employee_name_snapshot = models.CharField(
        max_length=255,
        help_text=(
            "Snapshot of the employee's full name "
            "at assignment time."
        ),
    )

    # ──────────────────────────────────────
    # ASSIGNMENT PERIOD
    # ──────────────────────────────────────

    assigned_date = models.DateField()

    returned_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Leave blank while the employee "
            "currently holds this asset."
        ),
    )

    assigned_condition = models.CharField(
        max_length=20,
        choices=AssetCondition.choices,
        default=AssetCondition.GOOD,
        help_text="Condition of the asset when assigned.",
    )

    returned_condition = models.CharField(
        max_length=20,
        choices=AssetCondition.choices,
        null=True,
        blank=True,
        help_text="Condition of the asset when returned.",
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    remarks = models.TextField(
        blank=True,
        default="",
    )

    assigned_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_assignments_made",
    )

    received_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asset_returns_received",
        help_text="Who processed the asset return.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-assigned_date",
        ]

        verbose_name = "Asset Assignment"

        verbose_name_plural = "Asset Assignments"

        constraints = [

            models.UniqueConstraint(
                fields=["asset"],
                condition=models.Q(returned_date__isnull=True),
                name="unique_active_assignment_per_asset",
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(returned_date__isnull=True)
                    | models.Q(returned_date__gte=models.F("assigned_date"))
                ),
                name="returned_date_after_assigned_date",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["asset"],
            ),

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["assigned_date"],
            ),

            models.Index(
                fields=["returned_date"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.remarks is not None:
            self.remarks = self.remarks.strip()

        if (
            self.returned_date
            and self.assigned_date
            and self.returned_date < self.assigned_date
        ):
            raise ValidationError(
                {
                    "returned_date":
                    (
                        "Returned date cannot be "
                        "earlier than assigned date."
                    )
                }
            )

        # Asset must belong to same company
        if (
            self.asset
            and self.company
            and self.asset.company != self.company
        ):
            raise ValidationError(
                {
                    "asset":
                    "Asset does not belong to this company."
                }
            )

        # Employee must belong to same company
        if (
            self.employee
            and self.company
            and self.employee.company != self.company
        ):
            raise ValidationError(
                {
                    "employee":
                    "Employee does not belong to this company."
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.remarks:
            self.remarks = self.remarks.strip()

        # Populate snapshots on first save only
        if not self.pk:

            if self.asset and not self.asset_tag_snapshot:
                self.asset_tag_snapshot = self.asset.asset_tag

            if self.employee and not self.employee_name_snapshot:
                self.employee_name_snapshot = (
                    self.employee.full_name
                )

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def is_active_assignment(self):
        """
        Returns True if the asset is currently
        held by this employee (not yet returned).
        """
        return self.returned_date is None

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        status = (
            "Active"
            if self.is_active_assignment
            else "Returned"
        )

        return (
            f"{self.asset_tag_snapshot}"
            f" → "
            f"{self.employee_name_snapshot}"
            f" ({status})"
        )
    

# ==========================================================
# MAINTENANCE TYPE
# ==========================================================

class MaintenanceType(models.TextChoices):
    REPAIR             = "Repair",             "Repair"
    CLEANING           = "Cleaning",           "Cleaning"
    UPGRADE            = "Upgrade",             "Upgrade"
    INSPECTION         = "Inspection",          "Inspection"
    PREVENTIVE         = "Preventive",          "Preventive Maintenance"
    OTHER              = "Other",               "Other"


# ==========================================================
# MAINTENANCE STATUS
# ==========================================================

class MaintenanceStatus(models.TextChoices):
    SCHEDULED   = "Scheduled",   "Scheduled"
    IN_PROGRESS = "In Progress", "In Progress"
    COMPLETED   = "Completed",   "Completed"
    CANCELLED   = "Cancelled",   "Cancelled"


# ==========================================================
# ASSET MAINTENANCE
# ==========================================================

class AssetMaintenance(models.Model):
    """
    Represents one maintenance event for an asset.

    Examples:
        Laptop sent for battery replacement
        Office chair sent for repair
        Printer scheduled for cleaning
        Annual inspection of network equipment

    Design:
        Like AssetAssignment, this is a history table.
        Every maintenance event is a permanent record,
        never edited away. An asset can have many
        maintenance records over its lifetime.

    Why track this separately from Asset.status?
        Asset.status = "Maintenance" tells you the
        CURRENT state. This table tells you the
        HISTORY of every repair, service, and
        inspection — including cost, vendor used,
        and outcome.

    Business rule:
        While a maintenance record is Scheduled or
        In Progress, the related Asset's status
        should be set to Maintenance by the service
        layer. When completed, the asset returns to
        Available (or Damaged/Retired if unrepairable).

    AI Readiness:
        This table enables questions like:
        - Repair frequency per asset/category
        - Average repair cost per vendor
        - Assets requiring frequent maintenance
          (candidates for replacement)
        - Total maintenance cost per department
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="asset_maintenances",
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="maintenance_records",
        help_text=(
            "Cannot delete an asset that has "
            "maintenance history."
        ),
    )

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_jobs",
        help_text="Vendor/service provider who performed the work.",
    )

    # ──────────────────────────────────────
    # SNAPSHOT
    # ──────────────────────────────────────

    asset_tag_snapshot = models.CharField(
        max_length=50,
        help_text=(
            "Snapshot of the asset tag at "
            "maintenance creation time."
        ),
    )

    # ──────────────────────────────────────
    # MAINTENANCE DETAILS
    # ──────────────────────────────────────

    maintenance_type = models.CharField(
        max_length=20,
        choices=MaintenanceType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.SCHEDULED,
    )

    description = models.TextField(
        help_text="What needs to be done / was done.",
    )

    scheduled_date = models.DateField()

    completed_date = models.DateField(
        null=True,
        blank=True,
    )

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    outcome_notes = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Result of the maintenance. "
            "e.g. Battery replaced successfully, "
            "Beyond repair, recommend retirement."
        ),
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    reported_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_reports_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-scheduled_date",
        ]

        verbose_name = "Asset Maintenance"

        verbose_name_plural = "Asset Maintenance Records"

        constraints = [

            models.CheckConstraint(
                condition=(
                    models.Q(completed_date__isnull=True)
                    | models.Q(completed_date__gte=models.F("scheduled_date"))
                ),
                name="completed_date_after_scheduled_date",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["asset"],
            ),

            models.Index(
                fields=["vendor"],
            ),

            models.Index(
                fields=["status"],
            ),

            models.Index(
                fields=["maintenance_type"],
            ),

            models.Index(
                fields=["scheduled_date"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.description is not None:
            self.description = self.description.strip()

        if self.outcome_notes is not None:
            self.outcome_notes = self.outcome_notes.strip()

        if not self.description:
            raise ValidationError(
                {
                    "description":
                    "Maintenance description is required."
                }
            )

        if (
            self.cost is not None
            and self.cost < 0
        ):
            raise ValidationError(
                {
                    "cost":
                    "Maintenance cost cannot be negative."
                }
            )

        if (
            self.completed_date
            and self.scheduled_date
            and self.completed_date < self.scheduled_date
        ):
            raise ValidationError(
                {
                    "completed_date":
                    (
                        "Completed date cannot be "
                        "earlier than scheduled date."
                    )
                }
            )

        # Status Completed requires completed_date
        if (
            self.status == MaintenanceStatus.COMPLETED
            and not self.completed_date
        ):
            raise ValidationError(
                {
                    "completed_date":
                    (
                        "Completed date is required "
                        "when status is Completed."
                    )
                }
            )

        # Asset must belong to same company
        if (
            self.asset
            and self.company
            and self.asset.company != self.company
        ):
            raise ValidationError(
                {
                    "asset":
                    "Asset does not belong to this company."
                }
            )

        # Vendor must belong to same company
        if (
            self.vendor
            and self.company
            and self.vendor.company != self.company
        ):
            raise ValidationError(
                {
                    "vendor":
                    "Vendor does not belong to this company."
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.description:
            self.description = self.description.strip()

        if self.outcome_notes:
            self.outcome_notes = self.outcome_notes.strip()

        if not self.pk and self.asset and not self.asset_tag_snapshot:
            self.asset_tag_snapshot = self.asset.asset_tag

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.asset_tag_snapshot}"
            f" - "
            f"{self.maintenance_type}"
            f" ({self.status})"
        )