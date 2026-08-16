"""
==========================================================
NexusERP-AI — Attendance Tools
==========================================================

AI tools for querying attendance reports and statistics.
All tools inherit from BaseTool and wrap AttendanceReportService.
"""

from datetime import date
from ai.tools.base import BaseTool, ToolContext, ToolResult
from attendance.reports import AttendanceReportService


# ==========================================================
# ATTENDANCE DASHBOARD TOOL
# ==========================================================

class AttendanceDashboardTool(BaseTool):
    """
    Returns today's high-level attendance KPIs.

    Answers questions like:
        How many employees are present today?
        What is today's attendance?
        How many employees are late or on leave today?
    """

    name = "attendance_dashboard"

    description = (
        "Returns today's live attendance KPIs: present count, absent count, "
        "late count, on leave count, half day count, not marked count, and "
        "attendance percentage. Best for questions like 'How many employees are present today?' "
        "or 'What is today's attendance?'."
    )

    def execute(
        self,
        context: ToolContext,
        dashboard_date=None,
        date=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes today's attendance dashboard KPI query.
        """
        service = AttendanceReportService(
            company=context.company,
        )

        target_date = date or dashboard_date or kwargs.get("date")
        data = service.dashboard(dashboard_date=target_date)

        if not data or data.get("total_employees", 0) == 0:
            return ToolResult(
                success=True,
                tool=self.name,
                data=data or {},
                message="No records found.",
            )

        present = data.get("present_count", 0)
        total = data.get("total_employees", 0)
        percentage = data.get("attendance_percentage", 0)

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Today {present} of {total} employees are present ({percentage}%).",
        )


# ==========================================================
# ATTENDANCE SUMMARY TOOL
# ==========================================================

class AttendanceSummaryTool(BaseTool):
    """
    Returns per-employee monthly attendance totals.

    Answers questions like:
        Show me attendance for June 2026.
        Which employees were absent most this month?
        What is the attendance summary for this month?
    """

    name = "attendance_summary"

    description = (
        "Returns per-employee attendance totals for a given month and year. "
        "Best for questions like 'Show me attendance for June 2026' or "
        "'Which employees were absent most this month?'."
    )

    def execute(
        self,
        context: ToolContext,
        month=None,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes monthly per-employee attendance summary query.
        """
        today = date.today()
        month_val = int(month) if month is not None else today.month
        year_val = int(year) if year is not None else today.year

        service = AttendanceReportService(
            company=context.company,
        )

        data = service.monthly_summary(month=month_val, year=year_val)

        if not data:
            return ToolResult(
                success=True,
                tool=self.name,
                data=[],
                message="No records found.",
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Returned {len(data)} employee attendance records for {month_val}/{year_val}.",
        )


# ==========================================================
# ATTENDANCE EXCEPTIONS TOOL
# ==========================================================

class AttendanceExceptionsTool(BaseTool):
    """
    Returns attendance records flagged as exceptions or anomalies.

    Answers questions like:
        Who came late today?
        Are there any missing checkouts?
        Which attendance records have pending approvals or manual entries?
    """

    name = "attendance_exceptions"

    description = (
        "Returns attendance records flagged as exceptions such as late arrivals, "
        "early exits, missing check-in, missing check-out, manual entries, and "
        "pending approvals. Best for 'Who came late today?' or 'Are there any missing checkouts?'."
    )

    def execute(
        self,
        context: ToolContext,
        date_from=None,
        date_to=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes attendance exceptions report query.
        """
        service = AttendanceReportService(
            company=context.company,
        )

        queryset = service.exceptions(
            date_from=date_from,
            date_to=date_to,
        )

        raw_records = list(
            queryset.values(
                "employee__employee_id",
                "date",
                "check_in",
                "check_out",
                "status",
                "late_minutes",
                "early_exit_minutes",
                "attendance_source",
                "attendance_modified",
                "approval_status",
            )
        )

        if not raw_records:
            return ToolResult(
                success=True,
                tool=self.name,
                data=[],
                message="No records found.",
            )

        data = []
        for record in raw_records:
            exception_types = []
            late = record.get("late_minutes", 0) or 0
            early = record.get("early_exit_minutes", 0) or 0
            check_in = record.get("check_in")
            check_out = record.get("check_out")
            source = record.get("attendance_source")
            modified = record.get("attendance_modified")
            approval = record.get("approval_status")

            if late > 0:
                exception_types.append("Late Arrival")
            if early > 0:
                exception_types.append("Early Exit")
            if check_in is None:
                exception_types.append("Missing Check-In")
            if check_out is None:
                exception_types.append("Missing Check-Out")
            if source == "Manual":
                exception_types.append("Manual Entry")
            if modified:
                exception_types.append("Modified Record")
            if approval == "Pending":
                exception_types.append("Pending Approval")

            data.append(
                {
                    "employee_id":        record.get("employee__employee_id"),
                    "check_in":           check_in,
                    "check_out":          check_out,
                    "status":             record.get("status"),
                    "late_minutes":       late,
                    "early_exit_minutes": early,
                    "exception_types":    exception_types,
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Found {len(data)} attendance exceptions.",
        )
