from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    LeaveBalance,
    LeaveRequest,
    LeaveType,
)

from django.db.models import Q

from .enums import (
    ApprovalStatus,
    LeaveStatus,
    LeaveSource,
)


# ==========================================================
# LEAVE SERVICE
# ==========================================================

class LeaveService:
    """
    Handles all leave management
    business logic.

    Responsibilities
    ----------------
    - Employee Validation
    - Leave Type Validation
    - Leave Balance Validation
    - Date Validation
    - Overlap Detection
    - Leave Application
    - Leave Approval
    - Leave Rejection
    - Leave Cancellation
    - Leave Balance Updates
    """

    def __init__(
        self,
        *,
        employee,
    ):
        self.employee = employee

    # ======================================================
    # EMPLOYEE VALIDATION
    # ======================================================

    def validate_employee(
        self,
    ):
        """
        Ensure the employee is active.
        """

        if not self.employee.is_active:
            raise ValidationError(
                "Inactive employees cannot apply for leave."
            )

        if not self.employee.company.is_active:
            raise ValidationError(
                "Employee company is inactive."
            )

        return self.employee

    # ======================================================
    # LEAVE TYPE VALIDATION
    # ======================================================

    def validate_leave_type(
        self,
        leave_type,
    ):
        """
        Validate the requested leave type.
        """

        if leave_type is None:
            raise ValidationError(
                "Leave type does not exist."
            )

        if not leave_type.is_active:
            raise ValidationError(
                "Selected leave type is inactive."
            )

        if (
            leave_type.company
            != self.employee.company
        ):
            raise ValidationError(
                (
                    "Selected leave type does "
                    "not belong to the employee's "
                    "company."
                )
            )

        return leave_type
    

        # ======================================================
    # LEAVE BALANCE
    # ======================================================

    def get_leave_balance(
        self,
        leave_type,
        year,
    ):
        """
        Return the employee's leave balance
        for the given leave type and year.
        """

        balance = (
            LeaveBalance.objects
            .select_related(
                "employee",
                "leave_type",
                "company",
            )
            .filter(
                employee=self.employee,
                leave_type=leave_type,
                company=self.employee.company,
                year=year,
            )
            .first()
        )

        if balance is None:
            raise ValidationError(
                (
                    "No leave balance found "
                    "for the selected leave type."
                )
            )

        return balance
    

        # ======================================================
    # LEAVE BALANCE VALIDATION
    # ======================================================

    def validate_leave_balance(
        self,
        balance,
        requested_days,
    ):
        """
        Ensure the employee has sufficient
        leave balance.
        """

        if requested_days <= Decimal("0.0"):
            raise ValidationError(
                "Requested leave days must be greater than zero."
            )

        if balance.remaining_days < requested_days:
            raise ValidationError(
                (
                    "Insufficient leave balance. "
                    f"Available: {balance.remaining_days}, "
                    f"Requested: {requested_days}."
                )
            )

        return balance
    

        # ======================================================
    # DATE VALIDATION
    # ======================================================

    def validate_dates(
        self,
        start_date,
        end_date,
    ):
        """
        Validate the requested leave dates.

        This method validates only the
        relationship between the supplied
        dates. Business rules such as
        backdated leave, holidays and
        weekends are handled separately.
        """

        if start_date is None:
            raise ValidationError(
                "Start date is required."
            )

        if end_date is None:
            raise ValidationError(
                "End date is required."
            )

        if end_date < start_date:
            raise ValidationError(
                (
                    "End date cannot be "
                    "earlier than start date."
                )
            )

        return (
            start_date,
            end_date,
        )
    

        # ======================================================
    # OVERLAP VALIDATION
    # ======================================================

    def validate_overlap(
        self,
        start_date,
        end_date,
    ):
        """
        Ensure the employee does not have
        another active leave request that
        overlaps the requested dates.
        """

        overlapping_leave = (
            LeaveRequest.objects
            .filter(
                employee=self.employee,
            )
            .filter(
                Q(
                    approval_status=ApprovalStatus.PENDING,
                )
                |
                Q(
                    approval_status=ApprovalStatus.APPROVED,
                )
            )
            .filter(
                start_date__lte=end_date,
                end_date__gte=start_date,
            )
            .first()
        )

        if overlapping_leave is not None:

            raise ValidationError(
                (
                    "The requested leave overlaps "
                    "with an existing leave request."
                )
            )

        return None
    

        # ======================================================
    # TOTAL LEAVE DAYS
    # ======================================================

    def calculate_total_days(
        self,
        start_date,
        end_date,
        is_half_day=False,
    ):
        """
        Calculate the total leave days.

        Version 1:
        - Counts calendar days.
        - Supports half-day leave.

        Future versions will exclude:
        - Holidays
        - Weekends
        - Company-specific non-working days
        """

        total_days = Decimal(
            (
                end_date - start_date
            ).days + 1
        )

        if is_half_day:
            total_days = Decimal("0.5")

        return total_days
    

        # ======================================================
    # APPLY LEAVE
    # ======================================================

    @transaction.atomic
    def apply_leave(
        self,
        *,
        leave_type,
        start_date,
        end_date,
        reason,
        is_half_day=False,
        remarks="",
        leave_source=LeaveSource.WEB,
    ):
        """
        Apply for leave.
        """

        # ------------------------------------------
        # Validations
        # ------------------------------------------

        self.validate_employee()

        leave_type = self.validate_leave_type(
            leave_type,
        )

        self.validate_dates(
            start_date,
            end_date,
        )

        self.validate_overlap(
            start_date,
            end_date,
        )

        total_days = self.calculate_total_days(
            start_date,
            end_date,
            is_half_day,
        )

        balance = self.get_leave_balance(
            leave_type=leave_type,
            year=start_date.year,
        )

        self.validate_leave_balance(
            balance,
            total_days,
        )

        # ------------------------------------------
        # Create Leave Request
        # ------------------------------------------

        leave_request = LeaveRequest.objects.create(
            company=self.employee.company,
            employee=self.employee,
            leave_type=leave_type,
            leave_type_snapshot=leave_type.leave_name,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            is_half_day=is_half_day,
            reason=reason,
            remarks=remarks,
            leave_source=leave_source,
        )

        return leave_request
    

        # ======================================================
    # DEDUCT LEAVE BALANCE
    # ======================================================

    def deduct_leave_balance(
        self,
        leave_request,
    ):
        """
        Deduct leave balance after
        leave approval.
        """

        if leave_request is None:
            raise ValidationError(
                "Leave request does not exist."
            )

        balance = self.get_leave_balance(
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year,
        )

        if (
            balance.remaining_days
            < leave_request.total_days
        ):
            raise ValidationError(
                (
                    "Insufficient leave balance "
                    "to approve this request."
                )
            )

        balance.used_days += (
            leave_request.total_days
        )

        balance.save()

        return balance
    

        # ======================================================
    # APPROVE LEAVE
    # ======================================================

    @transaction.atomic
    def approve_leave(
        self,
        *,
        leave_request,
        approved_by,
        approval_reason="",
    ):
        """
        Approve a leave request.
        """

        if leave_request is None:
            raise ValidationError(
                "Leave request does not exist."
            )

        if (
            leave_request.approval_status
            != ApprovalStatus.PENDING
        ):
            raise ValidationError(
                "Only pending leave requests can be approved."
            )

        self.deduct_leave_balance(
            leave_request,
        )

        leave_request.approval_status = (
            ApprovalStatus.APPROVED
        )

        leave_request.leave_status = (
            LeaveStatus.APPROVED
        )

        leave_request.approved_by = approved_by

        leave_request.approved_at = (
            timezone.now()
        )

        leave_request.approval_reason = (
            approval_reason.strip()
        )

        leave_request.save(
            update_fields=[
                "approval_status",
                "leave_status",
                "approved_by",
                "approved_at",
                "approval_reason",
                "updated_at",
            ]
        )

        return leave_request
    

        # ======================================================
    # REJECT LEAVE
    # ======================================================

    @transaction.atomic
    def reject_leave(
        self,
        *,
        leave_request,
        approved_by,
        approval_reason,
    ):
        """
        Reject a leave request.
        """

        if leave_request is None:
            raise ValidationError(
                "Leave request does not exist."
            )

        if (
            leave_request.approval_status
            != ApprovalStatus.PENDING
        ):
            raise ValidationError(
                "Only pending leave requests can be rejected."
            )

        leave_request.approval_status = (
            ApprovalStatus.REJECTED
        )

        leave_request.leave_status = (
            LeaveStatus.REJECTED
        )

        leave_request.approved_by = approved_by

        leave_request.approved_at = (
            timezone.now()
        )

        leave_request.approval_reason = (
            approval_reason.strip()
        )

        leave_request.save()

        return leave_request
    

        # ======================================================
    # RESTORE LEAVE BALANCE
    # ======================================================

    def restore_leave_balance(
        self,
        leave_request,
    ):
        """
        Restore leave balance after
        an approved leave request is cancelled.
        """

        if leave_request is None:
            raise ValidationError(
                "Leave request does not exist."
            )

        balance = self.get_leave_balance(
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year,
        )

        if (
            balance.used_days
            < leave_request.total_days
        ):
            raise ValidationError(
                (
                    "Leave balance cannot be "
                    "restored because the used "
                    "leave is less than the "
                    "requested leave."
                )
            )

        balance.used_days -= (
            leave_request.total_days
        )

        balance.save()

        return balance
    

        # ======================================================
    # CANCEL LEAVE
    # ======================================================

    @transaction.atomic
    def cancel_leave(
        self,
        *,
        leave_request,
        remarks="",
    ):
        """
        Cancel a leave request.
        """

        if leave_request is None:
            raise ValidationError(
                "Leave request does not exist."
            )

        if (
            leave_request.leave_status
            == LeaveStatus.CANCELLED
        ):
            raise ValidationError(
                "Leave request is already cancelled."
            )

        if (
            leave_request.approval_status
            == ApprovalStatus.REJECTED
        ):
            raise ValidationError(
                "Rejected leave requests cannot be cancelled."
            )

        # ------------------------------------------
        # Restore balance only if already approved
        # ------------------------------------------

        if (
            leave_request.approval_status
            == ApprovalStatus.APPROVED
        ):
            self.restore_leave_balance(
                leave_request,
            )

        # ------------------------------------------
        # Update leave status
        # ------------------------------------------

        leave_request.leave_status = (
            LeaveStatus.CANCELLED
        )

        if remarks.strip():
            if leave_request.remarks:
                leave_request.remarks += (
                    f"\nCancelled: {remarks.strip()}"
                )
            else:
                leave_request.remarks = (
                    f"Cancelled: {remarks.strip()}"
        )

        leave_request.save()

        return leave_request