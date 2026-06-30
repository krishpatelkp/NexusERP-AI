from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import (
    Asset,
    AssetAssignment,
    AssetMaintenance,
    AssetStatus,
    AssetCondition,
    MaintenanceStatus,
)


# ==========================================================
# INVENTORY SERVICE
# ==========================================================

class InventoryService:
    """
    Business logic for the Inventory module.

    Responsibilities
    ----------------
    - Asset Creation
    - Asset Assignment
    - Asset Return
    - Maintenance Scheduling
    - Maintenance Completion
    - Asset Retirement
    """

    def __init__(
        self,
        *,
        company,
    ):
        self.company = company

    # ======================================================
    # CREATE ASSET
    # ======================================================

    @transaction.atomic
    def create_asset(
        self,
        *,
        category,
        asset_tag,
        name,
        vendor=None,
        serial_number="",
        brand="",
        model="",
        description="",
        purchase_date=None,
        purchase_cost=None,
        warranty_expiry=None,
        invoice_number="",
        condition=AssetCondition.NEW,
        location="",
        notes="",
    ):
        """
        Create a new asset record.

        Validates that the category and vendor
        (if provided) belong to the same company
        before creating the asset.

        New assets always start with:
            status = Available
        """

        # ------------------------------------------
        # Validate category
        # ------------------------------------------

        if category is None:
            raise ValidationError(
                "Asset category is required."
            )

        if category.company != self.company:
            raise ValidationError(
                (
                    "Selected category does not "
                    "belong to this company."
                )
            )

        if not category.is_active:
            raise ValidationError(
                "Selected category is inactive."
            )

        # ------------------------------------------
        # Validate vendor (optional)
        # ------------------------------------------

        if vendor is not None:

            if vendor.company != self.company:
                raise ValidationError(
                    (
                        "Selected vendor does not "
                        "belong to this company."
                    )
                )

            if not vendor.is_active:
                raise ValidationError(
                    "Selected vendor is inactive."
                )

        # ------------------------------------------
        # Create Asset
        # ------------------------------------------

        asset = Asset.objects.create(
            company=self.company,
            category=category,
            vendor=vendor,
            asset_tag=asset_tag,
            name=name,
            serial_number=serial_number,
            brand=brand,
            model=model,
            description=description,
            purchase_date=purchase_date,
            purchase_cost=purchase_cost,
            warranty_expiry=warranty_expiry,
            invoice_number=invoice_number,
            status=AssetStatus.AVAILABLE,
            condition=condition,
            location=location,
            notes=notes,
        )

        return asset

    # ======================================================
    # ASSIGN ASSET
    # ======================================================

    @transaction.atomic
    def assign_asset(
        self,
        *,
        asset,
        employee,
        assigned_date=None,
        assigned_condition=AssetCondition.GOOD,
        assigned_by=None,
        remarks="",
    ):
        """
        Assign an asset to an employee.

        Validates
        ---------
        - Asset belongs to this company.
        - Employee belongs to this company.
        - Asset is active (not soft-deleted).
        - Employee is active (not resigned/terminated).
        - Asset status is Available.

        Concurrency
        -----------
        Uses select_for_update() to lock the asset row
        for the duration of this transaction. If two
        requests try to assign the same asset at the
        same time, the second one waits for the first
        to commit, then sees status != Available and
        fails with a clean validation error instead of
        creating a duplicate active assignment.

        The database-level partial unique constraint
        (unique_active_assignment_per_asset) is the
        final safety net even if this lock were ever
        bypassed.

        Side Effects
        ------------
        - Creates an AssetAssignment record.
        - Sets Asset.status = Assigned.
        - Sets Asset.condition = assigned_condition.

        Returns
        -------
        AssetAssignment
        """

        if assigned_date is None:
            assigned_date = timezone.localdate()

        # ------------------------------------------
        # Lock the asset row for this transaction
        # ------------------------------------------

        asset = (
            Asset.objects
            .select_for_update()
            .get(pk=asset.pk)
        )

        # ------------------------------------------
        # Validate asset
        # ------------------------------------------

        if asset.company != self.company:
            raise ValidationError(
                "Asset does not belong to this company."
            )

        if not asset.is_active:
            raise ValidationError(
                "This asset record is inactive."
            )

        if asset.status != AssetStatus.AVAILABLE:
            raise ValidationError(
                (
                    "Asset is not available for "
                    f"assignment. Current status: "
                    f"{asset.status}."
                )
            )

        # ------------------------------------------
        # Validate employee
        # ------------------------------------------

        if employee is None:
            raise ValidationError(
                "Employee is required."
            )

        if employee.company != self.company:
            raise ValidationError(
                (
                    "Employee does not belong "
                    "to this company."
                )
            )

        if not employee.is_active:
            raise ValidationError(
                (
                    "Cannot assign an asset to an "
                    "inactive employee."
                )
            )
        
        if assigned_by is not None:

            if assigned_by.company != self.company:
                raise ValidationError(
                "Assigned by user does not belong to this company."
            )

        # ------------------------------------------
        # Create Assignment
        # ------------------------------------------

        assignment = AssetAssignment.objects.create(
            company=self.company,
            asset=asset,
            employee=employee,
            asset_tag_snapshot=asset.asset_tag,
            employee_name_snapshot=employee.full_name,
            assigned_date=assigned_date,
            assigned_condition=assigned_condition,
            assigned_by=assigned_by,
            remarks=remarks,
        )

        # ------------------------------------------
        # Update Asset
        # ------------------------------------------

        asset.status = AssetStatus.ASSIGNED
        asset.condition = assigned_condition

        asset.save(
            update_fields=[
                "status",
                "condition",
                "updated_at",
            ]
        )

        return assignment
    # ======================================================
    # RETURN ASSET
    # ======================================================

    @transaction.atomic
    def return_asset(
        self,
        *,
        asset,
        returned_date=None,
        returned_condition=None,
        received_by=None,
        remarks="",
    ):
        """
        Return an asset from the employee currently
        holding it.

        Validates
        ---------
        - Asset belongs to this company.
        - Asset has an active (open) assignment.
        - That assignment has not already been returned.

        Concurrency
        -----------
        Locks both the Asset and the active
        AssetAssignment rows for the duration of
        this transaction, preventing a double-return
        or a return racing with a new assignment.

        Side Effects
        ------------
        - Sets AssetAssignment.returned_date.
        - Sets AssetAssignment.returned_condition
          (if provided).
        - Sets AssetAssignment.received_by.
        - Sets Asset.status = Available.
        - Sets Asset.condition = returned_condition
          (if provided), otherwise leaves the asset's
          condition unchanged.

        Returns
        -------
        AssetAssignment
            The closed assignment record.
        """

        if returned_date is None:
            returned_date = timezone.localdate()

        # ------------------------------------------
        # Lock the asset row
        # ------------------------------------------

        asset = (
            Asset.objects
            .select_for_update()
            .get(pk=asset.pk)
        )

        if asset.company != self.company:
            raise ValidationError(
                "Asset does not belong to this company."
            )

        # ------------------------------------------
        # Lock the active assignment row
        # ------------------------------------------

        assignment = (
            AssetAssignment.objects
            .select_for_update()
            .filter(
                asset=asset,
                returned_date__isnull=True,
            )
            .first()
        )

        if assignment is None:
            raise ValidationError(
                (
                    "This asset does not have an "
                    "active assignment to return."
                )
            )

        # ------------------------------------------
        # Validate dates
        # ------------------------------------------

        if returned_date < assignment.assigned_date:
            raise ValidationError(
                (
                    "Returned date cannot be earlier "
                    "than the assigned date."
                )
            )

        # ------------------------------------------
        # Close the assignment
        # ------------------------------------------

        assignment.returned_date = returned_date
        assignment.received_by = received_by

        if returned_condition is not None:
            assignment.returned_condition = returned_condition

        if remarks:
            if assignment.remarks:
                assignment.remarks += f"\nReturn: {remarks.strip()}"
            else:
                assignment.remarks = f"Return: {remarks.strip()}"

        assignment.save(
            update_fields=[
                "returned_date",
                "received_by",
                "returned_condition",
                "remarks",
                "updated_at",
            ]
        )

        # ------------------------------------------
        # Update the asset
        # ------------------------------------------

        asset.status = AssetStatus.AVAILABLE

        update_fields = [
            "status",
            "updated_at",
        ]

        if returned_condition is not None:
            asset.condition = returned_condition
            update_fields.append("condition")

        asset.save(update_fields=update_fields)

        return assignment


    # ======================================================
    # SCHEDULE MAINTENANCE
    # ======================================================

    @transaction.atomic
    def schedule_maintenance(
        self,
        *,
        asset,
        maintenance_type,
        description,
        scheduled_date=None,
        vendor=None,
        cost=None,
        outcome_notes="",
        reported_by=None,
    ):
        """
        Schedule maintenance for an asset.

        Validates
        ---------
        - Asset belongs to this company.
        - Asset is active.
        - Asset is not already under maintenance.
        - Asset is not retired.
        - Vendor (if provided) belongs to this company.
        - Vendor (if provided) is active.
        - Reported-by user (if provided) belongs to this company.

        Side Effects
        ------------
        - Creates an AssetMaintenance record.
        - Sets Asset.status = Maintenance.

        Returns
        -------
        AssetMaintenance
        """

        if scheduled_date is None:
            scheduled_date = timezone.localdate()

        # ------------------------------------------
        # Lock asset
        # ------------------------------------------

        asset = (
            Asset.objects
            .select_for_update()
            .get(pk=asset.pk)
        )

        # ------------------------------------------
        # Validate asset
        # ------------------------------------------

        if asset.company != self.company:
            raise ValidationError(
                "Asset does not belong to this company."
            )

        if not asset.is_active:
            raise ValidationError(
                "This asset record is inactive."
            )

        if asset.status == AssetStatus.MAINTENANCE:
            raise ValidationError(
                "Asset is already under maintenance."
            )

        if asset.status == AssetStatus.RETIRED:
            raise ValidationError(
                "Retired assets cannot be maintained."
            )

        # ------------------------------------------
        # Validate vendor
        # ------------------------------------------

        if vendor is not None:

            if vendor.company != self.company:
                raise ValidationError(
                    "Vendor does not belong to this company."
                )

            if not vendor.is_active:
                raise ValidationError(
                    "Vendor is inactive."
                )

        # ------------------------------------------
        # Validate reported_by
        # ------------------------------------------

        if reported_by is not None:

            if reported_by.company != self.company:
                raise ValidationError(
                    (
                        "Reported by user does not "
                        "belong to this company."
                    )
                )

        # ------------------------------------------
        # Create maintenance record
        # ------------------------------------------

        maintenance = AssetMaintenance.objects.create(
            company=self.company,
            asset=asset,
            vendor=vendor,
            asset_tag_snapshot=asset.asset_tag,
            maintenance_type=maintenance_type,
            status=MaintenanceStatus.SCHEDULED,
            description=description,
            scheduled_date=scheduled_date,
            cost=cost,
            outcome_notes=outcome_notes,
            reported_by=reported_by,
        )

        # ------------------------------------------
        # Update asset
        # ------------------------------------------

        asset.status = AssetStatus.MAINTENANCE

        asset.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return maintenance   
 

    # ======================================================
    # COMPLETE MAINTENANCE
    # ======================================================

    @transaction.atomic
    def complete_maintenance(
        self,
        *,
        maintenance,
        completed_date=None,
        asset_status=AssetStatus.AVAILABLE,
        asset_condition=None,
        outcome_notes="",
    ):
        """
        Complete a maintenance job.

        Validates
        ---------
        - Maintenance belongs to this company.
        - Maintenance is not already completed.
        - Maintenance is not cancelled.
        - Completed date is not earlier than scheduled date.

        Side Effects
        ------------
        - Marks maintenance as Completed.
        - Updates completed_date.
        - Updates outcome_notes.
        - Sets the asset status.
        - Optionally updates the asset condition.

        Returns
        -------
        AssetMaintenance
        """

        if completed_date is None:
            completed_date = timezone.localdate()

        # ------------------------------------------
        # Lock maintenance record
        # ------------------------------------------

        maintenance = (
            AssetMaintenance.objects
            .select_for_update()
            .select_related("asset")
            .get(pk=maintenance.pk)
        )

        asset = maintenance.asset

        # ------------------------------------------
        # Validate maintenance
        # ------------------------------------------

        if maintenance.company != self.company:
            raise ValidationError(
                "Maintenance record does not belong to this company."
            )

        if maintenance.status == MaintenanceStatus.COMPLETED:
            raise ValidationError(
                "Maintenance is already completed."
            )

        if maintenance.status == MaintenanceStatus.CANCELLED:
            raise ValidationError(
                "Cancelled maintenance cannot be completed."
            )

        if completed_date < maintenance.scheduled_date:
            raise ValidationError(
                (
                    "Completed date cannot be earlier "
                    "than scheduled date."
                )
            )

        # ------------------------------------------
        # Update maintenance
        # ------------------------------------------

        maintenance.status = MaintenanceStatus.COMPLETED
        maintenance.completed_date = completed_date

        if outcome_notes:
            maintenance.outcome_notes = outcome_notes.strip()

        maintenance.save(
            update_fields=[
                "status",
                "completed_date",
                "outcome_notes",
                "updated_at",
            ]
        )

        # ------------------------------------------
        # Update asset
        # ------------------------------------------

        asset.status = asset_status

        update_fields = [
            "status",
            "updated_at",
        ]

        if asset_condition is not None:
            asset.condition = asset_condition
            update_fields.append("condition")

        asset.save(update_fields=update_fields)

        return maintenance
    

    # ======================================================
    # RETIRE ASSET
    # ======================================================

    @transaction.atomic
    def retire_asset(
        self,
        *,
        asset,
        notes="",
    ):
        """
        Retire an asset permanently.

        Validates
        ---------
        - Asset belongs to this company.
        - Asset is active.
        - Asset is not currently assigned.
        - Asset is not already retired.

        Side Effects
        ------------
        - Sets Asset.status = Retired.
        - Appends retirement notes.

        Returns
        -------
        Asset
        """

        # ------------------------------------------
        # Lock asset
        # ------------------------------------------

        asset = (
            Asset.objects
            .select_for_update()
            .get(pk=asset.pk)
        )

        # ------------------------------------------
        # Validate asset
        # ------------------------------------------

        if asset.company != self.company:
            raise ValidationError(
                "Asset does not belong to this company."
            )

        if not asset.is_active:
            raise ValidationError(
                "This asset record is inactive."
            )

        if asset.status == AssetStatus.RETIRED:
            raise ValidationError(
                "Asset is already retired."
            )

        if asset.status == AssetStatus.ASSIGNED:
            raise ValidationError(
                (
                    "Assigned assets cannot be retired. "
                    "Return the asset first."
                )
            )

        # ------------------------------------------
        # Update notes
        # ------------------------------------------

        if notes:

            if asset.notes:
                asset.notes += (
                    f"\nRetirement: {notes.strip()}"
                )
            else:
                asset.notes = (
                    f"Retirement: {notes.strip()}"
                )

        # ------------------------------------------
        # Retire asset
        # ------------------------------------------

        asset.status = AssetStatus.RETIRED

        asset.save(
            update_fields=[
                "status",
                "notes",
                "updated_at",
            ]
        )

        return asset
