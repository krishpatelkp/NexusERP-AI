"""
==========================================================
NexusERP-AI — Payment Tools
==========================================================

AI tools for querying payment summaries and pending payments.
All tools inherit from BaseTool and wrap PaymentReportService.
"""

from ai.tools.base import BaseTool, ToolContext, ToolResult
from reports.services import PaymentReportService


# ==========================================================
# PAYMENT SUMMARY TOOL
# ==========================================================

class PaymentSummaryTool(BaseTool):
    """
    Returns high-level payment KPIs for a year.

    Answers questions like:
        How many payments were processed this year?
        What is our payment summary?
        How much money was paid out in 2026?
    """

    name = "payment_summary"

    description = (
        "Returns high-level payment KPIs for a year: total payments processed, "
        "total amount paid, pending payments count, failed count, and cancelled count. "
        "Best for 'How many payments were processed this year?' or 'Are there any payment statistics?'."
    )

    def execute(
        self,
        context: ToolContext,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes high-level yearly payment summary query.
        """
        year_val = int(year) if year is not None else None

        service = PaymentReportService(
            company=context.company,
        )

        data = service.payment_summary(year=year_val)

        total_payments = data.get("total_payments", 0) if data else 0

        if not data or total_payments == 0:
            return ToolResult(
                success=True,
                tool=self.name,
                data=data or {},
                message="No records found.",
            )

        total_paid = float(data.get("total_paid", 0) or 0)
        pending_count = data.get("pending_count", 0)
        formatted_paid = f"₹{total_paid:,.2f}"

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Total payments: {total_payments} ({formatted_paid} paid, {pending_count} pending).",
        )


# ==========================================================
# PENDING PAYMENTS TOOL
# ==========================================================

class PendingPaymentsTool(BaseTool):
    """
    Returns pending or processing salary payments.

    Answers questions like:
        Which employees have pending salary payments?
        Are there any pending payments?
        Show all payments awaiting processing.
    """

    name = "pending_payments"

    description = (
        "Returns all pending or processing payments awaiting completion. "
        "Best for 'Which employees have pending salary payments?' or 'Are there any pending payments?'."
    )

    def execute(
        self,
        context: ToolContext,
        **kwargs,
    ) -> ToolResult:
        """
        Executes pending payments query.
        """
        service = PaymentReportService(
            company=context.company,
        )

        queryset = service.pending_payments()

        raw_records = list(
            queryset.values(
                "payment_number",
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "employee__department__department_name",
                "amount",
                "status",
                "payment_method",
                "created_at",
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
                    "payment_number": item.get("payment_number"),
                    "employee_id":    item.get("employee__employee_id"),
                    "employee_name":  full_name,
                    "department":     item.get("employee__department__department_name"),
                    "amount":         item.get("amount"),
                    "status":         item.get("status"),
                    "payment_method": item.get("payment_method"),
                    "created_at":     item.get("created_at"),
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Found {len(data)} pending payments.",
        )
