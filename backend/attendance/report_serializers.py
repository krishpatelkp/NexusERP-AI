from rest_framework import serializers

from .models import Attendance


# ==========================================================
# BASE EMPLOYEE REPORT SERIALIZER
# ==========================================================

class BaseEmployeeReportSerializer(
    serializers.ModelSerializer,
):
    """
    Base serializer for attendance reports.

    Contains reusable employee and shift
    information shared across multiple
    attendance report serializers.
    """

    employee_id = serializers.CharField(
        source="employee.employee_id",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    department = serializers.CharField(
        source="employee.department.department_name",
        read_only=True,
        allow_null=True,
    )

    designation = serializers.CharField(
        source="employee.designation.designation_name",
        read_only=True,
        allow_null=True,
    )

    shift_name = serializers.CharField(
        source="shift.shift_name",
        read_only=True,
    )

    class Meta:

        model = Attendance

        fields = (
            "employee_id",
            "employee_name",
            "department",
            "designation",
            "shift_name",
        )

        read_only_fields = fields


# ==========================================================
# DAILY ATTENDANCE REPORT SERIALIZER
# ==========================================================

class DailyAttendanceReportSerializer(
    BaseEmployeeReportSerializer,
):
    """
    Serializer for the daily attendance report.

    Used by:
        GET /api/attendance/reports/daily/
    """

    class Meta(
        BaseEmployeeReportSerializer.Meta,
    ):

        fields = (
            "id",

            *BaseEmployeeReportSerializer.Meta.fields,

            "date",

            "check_in",

            "check_out",

            "working_minutes",

            "late_minutes",

            "early_exit_minutes",

            "overtime_minutes",

            "status",

            "attendance_source",

            "approval_status",
        )

        read_only_fields = fields


# ==========================================================
# EMPLOYEE ATTENDANCE HISTORY SERIALIZER
# ==========================================================

class EmployeeAttendanceHistorySerializer(
    BaseEmployeeReportSerializer,
):
    """
    Serializer for employee attendance history.
    """

    class Meta(
        BaseEmployeeReportSerializer.Meta,
    ):

        fields = (
            "id",

            *BaseEmployeeReportSerializer.Meta.fields,

            "date",

            "check_in",

            "check_out",

            "working_minutes",

            "late_minutes",

            "early_exit_minutes",

            "overtime_minutes",

            "status",

            "remarks",

            "attendance_source",

            "attendance_modified",

            "approval_status",
        )

        read_only_fields = fields


# ==========================================================
# MONTHLY ATTENDANCE SUMMARY SERIALIZER
# ==========================================================

class MonthlyAttendanceSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for monthly attendance summary.

    Used by:
        GET /api/attendance/reports/monthly/
    """

    employee_id = serializers.CharField()

    employee_name = serializers.CharField()

    department = serializers.CharField(
        allow_null=True,
    )

    designation = serializers.CharField(
        allow_null=True,
    )

    present_days = serializers.IntegerField()

    absent_days = serializers.IntegerField()

    half_days = serializers.IntegerField()

    leave_days = serializers.IntegerField()

    late_days = serializers.IntegerField()

    total_working_minutes = serializers.IntegerField()

    total_overtime_minutes = serializers.IntegerField()

    total_late_minutes = serializers.IntegerField()

    average_working_minutes = serializers.FloatField()

    attendance_percentage = serializers.FloatField()


# ==========================================================
# ATTENDANCE DASHBOARD SERIALIZER
# ==========================================================

class AttendanceDashboardSerializer(
    serializers.Serializer,
):
    """
    Serializer for attendance dashboard.

    Used by:
        GET /api/attendance/reports/dashboard/
    """

    date = serializers.DateField()

    total_employees = serializers.IntegerField()

    present_count = serializers.IntegerField()

    absent_count = serializers.IntegerField()

    late_count = serializers.IntegerField()

    on_leave_count = serializers.IntegerField()

    half_day_count = serializers.IntegerField()

    not_marked_count = serializers.IntegerField()

    attendance_percentage = serializers.FloatField()


# ==========================================================
# ATTENDANCE EXCEPTION SERIALIZER
# ==========================================================

class AttendanceExceptionSerializer(
    BaseEmployeeReportSerializer,
):
    """
    Serializer for attendance exceptions report.

    Used by:
        GET /api/attendance/reports/exceptions/
    """

    exception_types = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )

    class Meta(
        BaseEmployeeReportSerializer.Meta,
    ):

        fields = (
            "id",

            *BaseEmployeeReportSerializer.Meta.fields,

            "date",

            "check_in",

            "check_out",

            "working_minutes",

            "late_minutes",

            "early_exit_minutes",

            "overtime_minutes",

            "status",

            "attendance_source",

            "attendance_modified",

            "approval_status",

            "approval_reason",

            "remarks",

            "exception_types",
        )

        read_only_fields = fields