from django.core.exceptions import ValidationError
from django.db import models

from company.models import Company

from decimal import Decimal

from django.conf import settings
from django.db import models

from company.models import Company
from .enums import (
    ApprovalStatus,
    LeaveSource,
    LeaveStatus,
)


# ==========================================================
# LEAVE TYPE
# ==========================================================

class LeaveType(models.Model):
    """
    Represents a leave policy within a company.

    Examples:
        Casual Leave
        Sick Leave
        Earned Leave
        Maternity Leave
        Paternity Leave

    This model stores only leave policy information.
    Employee leave balances and requests are stored
    in separate models.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_types",
    )

    leave_name = models.CharField(
        max_length=100,
    )

    leave_code = models.CharField(
        max_length=20,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    max_days_per_year = models.PositiveSmallIntegerField()

    max_consecutive_days = models.PositiveSmallIntegerField()

    is_paid = models.BooleanField(
        default=True,
    )

    carry_forward = models.BooleanField(
        default=False,
    )

    requires_approval = models.BooleanField(
        default=True,
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
            "leave_name",
        ]

        verbose_name = "Leave Type"

        verbose_name_plural = "Leave Types"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "company",
                    "leave_name",
                ],
                name="unique_leave_name_per_company",
            ),

            models.UniqueConstraint(
                fields=[
                    "company",
                    "leave_code",
                ],
                name="unique_leave_code_per_company",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["leave_code"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    def clean(self):

        super().clean()

        if self.leave_name is not None:
            self.leave_name = self.leave_name.strip()

        if self.leave_code is not None:
            self.leave_code = self.leave_code.strip()

        if self.description is not None:
            self.description = self.description.strip()

        if not self.leave_name:
            raise ValidationError(
                {
                    "leave_name":
                    "Leave name is required."
                }
            )

        if not self.leave_code:
            raise ValidationError(
                {
                    "leave_code":
                    "Leave code is required."
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ):

        if self.leave_name:
            self.leave_name = self.leave_name.strip()

        if self.leave_code:
            self.leave_code = (
                self.leave_code
                .strip()
                .upper()
            )

        if self.description:
            self.description = (
                self.description.strip()
            )

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.company.company_name}"
            f" - "
            f"{self.leave_name}"
        )
    

# ==========================================================
# LEAVE BALANCE
# ==========================================================

class LeaveBalance(models.Model):
    """
    Stores yearly leave balance for an employee.

    One record exists per:

        Employee
        Leave Type
        Year

    Remaining leave is automatically calculated from:

        Allocated - Used

    This model is optimized for fast payroll,
    employee dashboards, and AI analytics.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_balances",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_balances",
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name="employee_balances",
    )

    year = models.PositiveSmallIntegerField()

    allocated_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
    )

    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
    )

    remaining_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "employee",
            "leave_type",
            "-year",
        ]

        verbose_name = "Leave Balance"

        verbose_name_plural = "Leave Balances"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "employee",
                    "leave_type",
                    "year",
                ],
                name="unique_leave_balance_per_year",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["leave_type"],
            ),

            models.Index(
                fields=["year"],
            ),

        ]

    def clean(self):

        super().clean()

        if self.used_days > self.allocated_days:

            raise ValidationError(
                {
                    "used_days":
                    (
                        "Used leave cannot exceed "
                        "allocated leave."
                    )
                }
            )

        self.remaining_days = (
            self.allocated_days -
            self.used_days
        )

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" - "
            f"{self.leave_type.leave_name}"
            f" ({self.year})"
        )
    

# ==========================================================
# LEAVE REQUEST
# ==========================================================

class LeaveRequest(models.Model):
    """
    Represents a leave request submitted by an employee.

    This model stores the complete lifecycle of a leave
    request, from submission through approval or rejection.

    It is designed to be:

    • Multi-company
    • AI-ready
    • Payroll-ready
    • Attendance-ready
    • Audit-friendly
    • Scalable
    """

    # ======================================================
    # COMPANY & EMPLOYEE
    # ======================================================

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )

    # ======================================================
    # LEAVE INFORMATION
    # ======================================================

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name="leave_requests",
    )

    leave_type_snapshot = models.CharField(
        max_length=100,
    )

    # ======================================================
    # LEAVE DURATION
    # ======================================================

    start_date = models.DateField()

    end_date = models.DateField()

    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0.0"),
    )

    is_half_day = models.BooleanField(
        default=False,
    )

    # ======================================================
    # EMPLOYEE INPUT
    # ======================================================

    reason = models.TextField()

    remarks = models.TextField(
        blank=True,
        default="",
    )

    # ======================================================
    # STATUS
    # ======================================================

    leave_status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING,
    )

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )

    # ======================================================
    # APPROVAL
    # ======================================================

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_requests",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approval_reason = models.TextField(
        blank=True,
        default="",
    )

    # ======================================================
    # AI & AUDIT
    # ======================================================

    leave_source = models.CharField(
        max_length=20,
        choices=LeaveSource.choices,
        default=LeaveSource.WEB,
    )

    leave_modified = models.BooleanField(
        default=False,
    )

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modified_leave_requests",
    )

    request_date = models.DateField(
        auto_now_add=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-start_date",
            "-created_at",
        ]

        verbose_name = "Leave Request"

        verbose_name_plural = "Leave Requests"

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["leave_type"],
            ),

            models.Index(
                fields=["start_date"],
            ),

            models.Index(
                fields=["end_date"],
            ),

            models.Index(
                fields=["leave_status"],
            ),

            models.Index(
                fields=["approval_status"],
            ),

            models.Index(
                fields=["request_date"],
            ),

        ]

        constraints = [

            models.CheckConstraint(
                condition=models.Q(
                    end_date__gte=models.F(
                        "start_date",
                    ),
                ),
                name="leave_end_after_start_date",
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.reason is not None:
            self.reason = self.reason.strip()

        if self.remarks is not None:
            self.remarks = self.remarks.strip()

        if self.approval_reason is not None:
            self.approval_reason = (
                self.approval_reason.strip()
            )

        if not self.leave_type_snapshot and self.leave_type:
            self.leave_type_snapshot = (
                self.leave_type.leave_name
            )

        if (
            self.end_date
            and self.start_date
            and self.end_date < self.start_date
        ):

            raise ValidationError(
                {
                    "end_date":
                    (
                        "End date cannot be "
                        "earlier than start date."
                    )
                }
            )

        if self.total_days < Decimal("0.0"):

            raise ValidationError(
                {
                    "total_days":
                    (
                        "Total leave days "
                        "cannot be negative."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        # Populate snapshot fields
        if (
            not self.leave_type_snapshot
            and self.leave_type
        ):
            self.leave_type_snapshot = (
            self.leave_type.leave_name
        )

        self.full_clean()

        super().save(
            *args,
            **kwargs,
    )

    # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" - "
            f"{self.leave_type_snapshot}"
            f" ({self.start_date} → {self.end_date})"
        )