"""
==========================================================
NexusERP-AI — Leave Tools
==========================================================

AI tools for querying leave statistics, balances, and pending requests.
All tools inherit from BaseTool and wrap LeaveReportService.
"""

from ai.tools.base import BaseTool, ToolContext, ToolResult
from reports.services import LeaveReportService


# ==========================================================
# LEAVE SUMMARY TOOL
# ==========================================================

class LeaveSummaryTool(BaseTool):
    """
    Returns high-level leave statistics for a year.

    Answers questions like:
        How many leaves were approved this year?
        What is the leave utilization?
        How many pending leave requests are there for 2026?
    """

    name = "leave_summary"

    description = (
        "Returns high-level leave statistics for a year: total requests, "
        "approved count, pending count, rejected count, and total days taken. "
        "Best for questions like 'How many leaves were approved this year?' or "
        "'What is the leave utilization?'."
    )

    def execute(
        self,
        context: ToolContext,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes high-level yearly leave summary query.
        """
        year_val = int(year) if year is not None else None

        service = LeaveReportService(
            company=context.company,
        )

        data = service.leave_summary(year=year_val)

        if not data or data.get("total_requests", 0) == 0:
            return ToolResult(
                success=True,
                tool=self.name,
                data=data or {},
                message="No records found.",
            )

        total_requests = data.get("total_requests", 0)
        approved = data.get("approved", 0)

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Total leave requests: {total_requests} ({approved} approved).",
        )


# ==========================================================
# LEAVE BALANCE TOOL
# ==========================================================

class LeaveBalanceTool(BaseTool):
    """
    Returns current leave balances for active employees.

    Answers questions like:
        Show me leave balances.
        How many sick leaves does Engineering have left?
        What is the remaining leave balance for active employees?
    """

    name = "leave_balance"

    description = (
        "Returns current leave balances for all active employees with optional "
        "filters for department and leave type. Best for 'Show me leave balances' "
        "or 'How many sick leaves does Engineering have left?'."
    )

    def execute(
        self,
        context: ToolContext,
        department_id=None,
        leave_type_id=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes employee leave balance report query.
        """
        service = LeaveReportService(
            company=context.company,
        )

        queryset = service.leave_balance_report(
            department_id=department_id,
            leave_type_id=leave_type_id,
        )

        raw_records = list(
            queryset.values(
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "leave_type__leave_name",
                "remaining_days",
                "used_days",
                "allocated_days",
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
        for item in raw_records:
            first = item.get("employee__first_name") or ""
            last = item.get("employee__last_name") or ""
            full_name = f"{first} {last}".strip()

            data.append(
                {
                    "employee_id":     item.get("employee__employee_id"),
                    "full_name":       full_name,
                    "leave_type":      item.get("leave_type__leave_name"),
                    "balance_days":    item.get("remaining_days"),
                    "used_days":       item.get("used_days"),
                    "allocated_days":  item.get("allocated_days"),
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Returned {len(data)} leave balance records.",
        )


# ==========================================================
# PENDING LEAVES TOOL
# ==========================================================

class PendingLeavesTool(BaseTool):
    """
    Returns pending leave requests awaiting approval.

    Answers questions like:
        How many leave requests need approval?
        Show me pending leaves.
        Which leave requests are pending?
    """

    name = "pending_leaves"

    description = (
        "Returns all pending leave requests awaiting approval. "
        "Best for 'How many leave requests need approval?' or 'Show me pending leaves'."
    )

    def execute(
        self,
        context: ToolContext,
        **kwargs,
    ) -> ToolResult:
        """
        Executes pending leave requests query.
        """
        service = LeaveReportService(
            company=context.company,
        )

        queryset = service.leave_history(status="Pending")

        raw_records = list(
            queryset.values(
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "leave_type__leave_name",
                "start_date",
                "end_date",
                "total_days",
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
        for item in raw_records:
            first = item.get("employee__first_name") or ""
            last = item.get("employee__last_name") or ""
            full_name = f"{first} {last}".strip()

            data.append(
                {
                    "employee_id": item.get("employee__employee_id"),
                    "full_name":   full_name,
                    "leave_type":  item.get("leave_type__leave_name"),
                    "start_date":  item.get("start_date"),
                    "end_date":    item.get("end_date"),
                    "total_days":  item.get("total_days"),
                    "status":      item.get("approval_status"),
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Found {len(data)} pending leave requests.",
        )
