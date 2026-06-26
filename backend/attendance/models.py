from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from company.models import Company



# ==========================================================
# HOLIDAY TYPE
# ==========================================================

class HolidayType(models.TextChoices):
    NATIONAL = "National", "National Holiday"
    FESTIVAL = "Festival", "Festival"
    COMPANY = "Company", "Company Holiday"
    OPTIONAL = "Optional", "Optional Holiday"
    OTHER = "Other", "Other"


# ==========================================================
# ATTENDANCE STATUS
# ==========================================================

class AttendanceStatus(models.TextChoices):
    PRESENT = "Present", "Present"
    ABSENT = "Absent", "Absent"
    HALF_DAY = "Half Day", "Half Day"
    LEAVE = "Leave", "Leave"
    HOLIDAY = "Holiday", "Holiday"
    WEEK_OFF = "Week Off", "Week Off"
    WORK_FROM_HOME = "Work From Home", "Work From Home"


class AttendanceSource(models.TextChoices):
    MANUAL    = "Manual",    "Manual"
    WEB       = "Web",       "Web"
    MOBILE    = "Mobile",    "Mobile"
    BIOMETRIC = "Biometric", "Biometric"
    API       = "API",       "API"


class ApprovalStatus(models.TextChoices):
    PENDING  = "Pending",  "Pending"
    APPROVED = "Approved", "Approved"
    REJECTED = "Rejected", "Rejected"

# ==========================================================
# HOLIDAY MODEL
# ==========================================================

class Holiday(models.Model):
    """
    Stores holidays for a company.

    Used by:
    - Attendance
    - Leave Management
    - Payroll
    - Reports
    - AI Analytics
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="holidays",
    )

    name = models.CharField(
        max_length=150,
    )

    date = models.DateField()

    holiday_type = models.CharField(
        max_length=20,
        choices=HolidayType.choices,
        default=HolidayType.NATIONAL,
    )

    description = models.TextField(
        blank=True,
    )

    is_optional = models.BooleanField(
        default=False,
        help_text="Employees may choose to take this holiday.",
    )

    is_recurring = models.BooleanField(
        default=True,
        help_text="Whether this holiday repeats every year.",
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

        ordering = (
            "date",
            "name",
        )

        verbose_name = "Holiday"

        verbose_name_plural = "Holidays"

        constraints = [

            models.UniqueConstraint(
                fields=(
                    "company",
                    "date",
                ),
                name="unique_holiday_per_company_per_date",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["date"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    def clean(self):
        """
        Business validation.
        """

        super().clean()

        self.name = self.name.strip()

        self.description = self.description.strip()

        if not self.name:

            raise ValidationError(
                {
                    "name":
                    "Holiday name cannot be empty."
                }
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
            f"{self.name}"
            f" ({self.date})"
        )
    

# ==========================================================
# ATTENDANCE MODEL
# ==========================================================

from employees.models import (
    Employee,
    Shift,
)


class Attendance(models.Model):
    """
    Stores employee attendance.

    Used by:
    - Leave
    - Payroll
    - Reports
    - AI Analytics
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="attendances",
    )

    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name="attendances",
    )

    date = models.DateField()

    scheduled_start_time = models.TimeField()

    scheduled_end_time = models.TimeField()

    scheduled_grace_minutes = models.PositiveIntegerField(null=True, blank=True)

    check_in = models.DateTimeField(
        null=True,
        blank=True,
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
    )

    working_minutes = models.PositiveIntegerField(
        default=0,
    )

    late_minutes = models.PositiveIntegerField(
        default=0,
    )

    early_exit_minutes = models.PositiveIntegerField(
        default=0,
    )

    overtime_minutes = models.PositiveIntegerField(
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.ABSENT,
    )

    remarks = models.TextField(
        blank=True,
    )

    # ──────────────────────────────────────
    # SNAPSHOT FIELDS
    # ──────────────────────────────────────

    shift_name_snapshot = models.CharField(
        max_length=100,
        blank=True,
        help_text="Shift name at the time attendance was recorded.",
    )

    # ──────────────────────────────────────
    # ATTENDANCE SOURCE
    # ──────────────────────────────────────

    attendance_source = models.CharField(
        max_length=20,
        choices=AttendanceSource.choices,
        default=AttendanceSource.WEB,
    )

    attendance_modified = models.BooleanField(
        default=False,
        help_text="True if this record was modified after creation.",
    )

    # ──────────────────────────────────────
    # APPROVAL
    # ──────────────────────────────────────

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.APPROVED,
        help_text="Approval status of this attendance record.",
    )

    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_attendances",
        help_text="User who approved this attendance record.",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this attendance record was approved.",
    )

    approval_reason = models.TextField(
        blank=True,
        help_text="Reason for approval or rejection.",
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

        ordering = (
            "-date",
            "employee",
        )

        verbose_name = "Attendance"

        verbose_name_plural = "Attendance"

        constraints = [

            models.UniqueConstraint(
                fields=(
                    "employee",
                    "date",
                ),
                name="unique_attendance_per_employee_per_day",
            ),

        ]

        indexes = [

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["date"],
            ),

            models.Index(
                fields=["status"],
            ),

            models.Index(
                fields=["is_active"],
            ),
            models.Index(fields=["attendance_source"]),
            models.Index(fields=["approval_status"]),
            models.Index(fields=["attendance_modified"]),

        ]

    def clean(self):

        super().clean()

        self.remarks = self.remarks.strip()

    def save(
        self,
        *args,
        **kwargs,
    ):
        """
        Snapshot shift details when creating attendance.
        """

        if self.shift:

            if self.scheduled_start_time is None:
                self.scheduled_start_time = self.shift.start_time

            if self.scheduled_end_time is None:
                self.scheduled_end_time = self.shift.end_time

            if self.scheduled_grace_minutes is None:
                self.scheduled_grace_minutes = (
                    self.shift.grace_minutes
                )

            if not self.shift_name_snapshot:
                self.shift_name_snapshot = self.shift.shift_name

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):

        return (
            f"{self.employee} - "
            f"{self.date}"
        )