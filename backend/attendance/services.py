from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from employees.models import (
    EmployeeShiftAssignment,
)

from .models import (
    Attendance,
    AttendanceStatus,
    Holiday,
)


# ==========================================================
# ATTENDANCE CALCULATION SERVICE
# ==========================================================

class AttendanceCalculationService:
    """
    Handles all attendance business logic.

    Responsibilities
    ----------------
    - Employee Validation
    - Shift Resolution
    - Holiday Detection
    - Attendance Creation
    - Check-In
    - Check-Out
    - Working Minutes Calculation
    - Late Minutes Calculation
    - Early Exit Calculation
    - Overtime Calculation
    - Attendance Status Calculation
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

    def validate_employee(self):
        """
        Ensure employee is active.
        """

        if not self.employee.is_active:
            raise ValidationError(
                "Inactive employees cannot mark attendance."
            )

    # ======================================================
    # ACTIVE SHIFT
    # ======================================================

    def get_active_shift(self):
        """
        Returns the employee's active shift assignment.
        Falls back to company active shift or default General Shift if none explicitly assigned.
        """
        from employees.models import Shift
        from datetime import time

        assignment = (
            EmployeeShiftAssignment.objects
            .select_related("shift")
            .filter(
                employee=self.employee,
                is_active=True,
            )
            .first()
        )

        if assignment:
            return assignment.shift

        company_shift = Shift.objects.filter(
            company=self.employee.company,
            is_active=True,
        ).first()

        eff_date = self.employee.joining_date or timezone.localdate()

        if company_shift:
            EmployeeShiftAssignment.objects.create(
                employee=self.employee,
                shift=company_shift,
                effective_from=eff_date,
                is_active=True,
            )
            return company_shift

        default_shift, _ = Shift.objects.get_or_create(
            company=self.employee.company,
            shift_name="General Shift",
            defaults={
                "shift_code": "GEN",
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "is_active": True,
            }
        )
        EmployeeShiftAssignment.objects.create(
            employee=self.employee,
            shift=default_shift,
            effective_from=eff_date,
            is_active=True,
        )
        return default_shift

    # ======================================================
    # HOLIDAY CHECK
    # ======================================================

    def is_holiday(self, attendance_date):
        """
        Returns True if the attendance date
        is a company holiday.
        """

        return Holiday.objects.filter(
            company=self.employee.company,
            date=attendance_date,
            is_active=True,
        ).exists()

    # ======================================================
    # GET OR CREATE ATTENDANCE
    # ======================================================

    @transaction.atomic
    def get_or_create_attendance(self, attendance_date=None):
        """
        Returns attendance for a given date.
        Creates attendance if it does not exist.
        """

        self.validate_employee()

        if attendance_date is None:
            attendance_date = timezone.localdate()

        shift = self.get_active_shift()

        attendance, created = Attendance.objects.get_or_create(
            employee=self.employee,
            date=attendance_date,
            defaults={
                "shift": shift,
                "scheduled_start_time": shift.start_time,
                "scheduled_end_time": shift.end_time,
                "scheduled_grace_minutes": shift.grace_minutes,
                "status": AttendanceStatus.ABSENT,
            },
        )

        return attendance

    # ======================================================
    # CHECK-IN
    # ======================================================

    @transaction.atomic
    def process_check_in(self, check_in, remarks=""):
        """
        Process employee check-in.
        """

        attendance = self.get_or_create_attendance()

        if attendance.check_in:
            raise ValidationError(
                "Employee has already checked in today."
            )

        attendance.check_in = check_in

        if remarks:
            attendance.remarks = remarks.strip()

        attendance.save()

        return attendance

    # ======================================================
    # CHECK-OUT
    # ======================================================

    @transaction.atomic
    def process_check_out(self, check_out, remarks=""):
        """
        Process employee check-out.
        """

        attendance = self.get_or_create_attendance()

        if attendance.check_in is None:
            raise ValidationError(
                "Employee has not checked in today."
            )

        if attendance.check_out is not None:
            raise ValidationError(
                "Employee has already checked out today."
            )

        if check_out < attendance.check_in:
            raise ValidationError(
                "Check-out time cannot be before check-in."
            )

        attendance.check_out = check_out

        if remarks:
            attendance.remarks = remarks.strip()

        self.finalize_attendance(attendance)

        return attendance

    # ======================================================
    # WORKING MINUTES
    # ======================================================

    def calculate_working_minutes(self, attendance):
        """
        Calculate total working minutes.
        """

        if (
            attendance.check_in is None
            or attendance.check_out is None
        ):
            return 0

        working_minutes = int(
            (
                attendance.check_out
                - attendance.check_in
            ).total_seconds() // 60
        )

        attendance.working_minutes = max(working_minutes, 0)

        return attendance.working_minutes

    # ======================================================
    # LATE MINUTES
    # ======================================================

    def calculate_late_minutes(self, attendance):
        """
        Calculate employee late minutes.
        """

        if attendance.check_in is None:
            return 0

        scheduled_start = datetime.combine(
            attendance.date,
            attendance.scheduled_start_time,
        )

        scheduled_start = timezone.make_aware(scheduled_start)

        allowed_check_in = scheduled_start + timedelta(
            minutes=attendance.scheduled_grace_minutes,
        )

        if attendance.check_in <= allowed_check_in:
            attendance.late_minutes = 0
        else:
            attendance.late_minutes = int(
                (
                    attendance.check_in - allowed_check_in
                ).total_seconds() // 60
            )

        return attendance.late_minutes

    # ======================================================
    # EARLY EXIT MINUTES
    # ======================================================

    def calculate_early_exit_minutes(self, attendance):
        """
        Calculate employee early exit minutes.
        """

        if attendance.check_out is None:
            return 0

        scheduled_end = datetime.combine(
            attendance.date,
            attendance.scheduled_end_time,
        )

        scheduled_end = timezone.make_aware(scheduled_end)

        if attendance.check_out >= scheduled_end:
            attendance.early_exit_minutes = 0
        else:
            attendance.early_exit_minutes = int(
                (
                    scheduled_end - attendance.check_out
                ).total_seconds() // 60
            )

        return attendance.early_exit_minutes

    # ======================================================
    # OVERTIME MINUTES
    # ======================================================

    def calculate_overtime_minutes(self, attendance):
        """
        Calculate employee overtime minutes.
        """

        if attendance.check_out is None:
            return 0

        scheduled_end = datetime.combine(
            attendance.date,
            attendance.scheduled_end_time,
        )

        scheduled_end = timezone.make_aware(scheduled_end)

        if attendance.check_out <= scheduled_end:
            attendance.overtime_minutes = 0
        else:
            attendance.overtime_minutes = int(
                (
                    attendance.check_out - scheduled_end
                ).total_seconds() // 60
            )

        return attendance.overtime_minutes

    # ======================================================
    # ATTENDANCE STATUS
    # ======================================================

    def determine_attendance_status(self, attendance):
        """
        Determine attendance status based on working minutes.
        Thresholds are read from constants so they can be
        changed in one place.
        """

        from attendance.constants import (
            FULL_DAY_MINUTES,
            HALF_DAY_MINUTES,
        )

        if attendance.check_in is None:
            attendance.status = AttendanceStatus.ABSENT

        elif attendance.working_minutes >= FULL_DAY_MINUTES:
            attendance.status = AttendanceStatus.PRESENT

        elif attendance.working_minutes >= HALF_DAY_MINUTES:
            attendance.status = AttendanceStatus.HALF_DAY

        else:
            attendance.status = AttendanceStatus.ABSENT

        return attendance.status

    # ======================================================
    # FINALIZE ATTENDANCE
    # ======================================================

    def finalize_attendance(self, attendance):
        """
        Perform all attendance calculations.
        """

        self.calculate_working_minutes(attendance)
        self.calculate_late_minutes(attendance)
        self.calculate_early_exit_minutes(attendance)
        self.calculate_overtime_minutes(attendance)
        self.determine_attendance_status(attendance)

        attendance.save()

        return attendance