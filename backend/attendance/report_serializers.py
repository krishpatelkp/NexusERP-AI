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
    )

    designation = serializers.CharField(
        source="employee.designation.designation_name",
        read_only=True,
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
    Serializer for daily attendance report.
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