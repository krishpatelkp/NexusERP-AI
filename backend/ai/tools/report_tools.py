"""
==========================================================
NexusERP-AI — Report Tools
==========================================================

AI tools for querying enterprise trends: headcount changes,
payroll costs, and asset maintenance costs.
All tools inherit from BaseTool and wrap report service classes.
"""

from ai.tools.base import BaseTool, ToolContext, ToolResult
from reports.services import (
    EmployeeReportService,
    PayrollReportService,
    InventoryReportService,
)


# ==========================================================
# HEADCOUNT TREND TOOL
# ==========================================================

class HeadcountTrendTool(BaseTool):
    """
    Returns monthly headcount joinings trend for a year.

    Answers questions like:
        How has headcount changed this year?
        Show employee joining trends.
        Are we hiring more employees this year?
    """

    name = "headcount_trend"

    description = (
        "Returns monthly headcount joinings trend for a year. "
        "Best for 'How has headcount changed this year?' or 'Show employee joining trends'."
    )

    def execute(
        self,
        context: ToolContext,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes monthly headcount trend query.
        """
        year_val = int(year) if year is not None else None

        service = EmployeeReportService(
            company=context.company,
        )

        queryset = service.headcount_trend(year=year_val)

        raw_records = list(
            queryset.values("month", "joinings")
        )

        if not raw_records:
            return ToolResult(
                success=True,
                tool=self.name,
                data=[],
                message="No records found.",
            )

        data = []
        total_joinings = 0
        for item in raw_records:
            j = item.get("joinings", 0) or 0
            total_joinings += j
            data.append(
                {
                    "month":    item.get("month"),
                    "joinings": j,
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Returned headcount trend across {len(data)} months (total {total_joinings} joinings).",
        )


# ==========================================================
# PAYROLL TREND TOOL
# ==========================================================

class PayrollTrendTool(BaseTool):
    """
    Returns monthly payroll cost trend.

    Answers questions like:
        Is payroll cost increasing month by month?
        Show payroll trend.
        How has salary spending changed over the year?
    """

    name = "payroll_trend"

    description = (
        "Returns month-by-month payroll cost trend (total gross, total net, employee count) for a year. "
        "Best for 'Is payroll cost increasing month by month?' or 'Show payroll trend'."
    )

    def execute(
        self,
        context: ToolContext,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes monthly payroll cost trend query.
        """
        year_val = int(year) if year is not None else None

        service = PayrollReportService(
            company=context.company,
        )

        queryset = service.payroll_trend(year=year_val)

        raw_records = list(
            queryset.values(
                "month",
                "total_gross",
                "total_net",
                "employee_count",
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
            data.append(
                {
                    "month":          item.get("month"),
                    "total_gross":    item.get("total_gross"),
                    "total_net":      item.get("total_net"),
                    "employee_count": item.get("employee_count"),
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Returned payroll trend across {len(data)} months.",
        )


# ==========================================================
# MAINTENANCE COST TREND TOOL
# ==========================================================

class MaintenanceCostTrendTool(BaseTool):
    """
    Returns monthly asset maintenance cost trend.

    Answers questions like:
        Are repair costs rising?
        Show maintenance cost trend.
        How much are we spending on asset repairs each month?
    """

    name = "maintenance_cost_trend"

    description = (
        "Returns monthly completed asset maintenance repair costs and count trend for a year. "
        "Best for 'Are repair costs rising?' or 'Show maintenance cost trend'."
    )

    def execute(
        self,
        context: ToolContext,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes monthly maintenance repair cost trend query.
        """
        year_val = int(year) if year is not None else None

        service = InventoryReportService(
            company=context.company,
        )

        queryset = service.maintenance_cost_trend(year=year_val)

        raw_records = list(
            queryset.values("month", "total_cost", "repair_count")
        )

        if not raw_records:
            return ToolResult(
                success=True,
                tool=self.name,
                data=[],
                message="No records found.",
            )

        data = []
        total_repairs = 0
        for item in raw_records:
            r = item.get("repair_count", 0) or 0
            total_repairs += r
            data.append(
                {
                    "month":        item.get("month"),
                    "total_cost":   item.get("total_cost"),
                    "repair_count": r,
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Returned maintenance cost trend across {len(data)} months ({total_repairs} repairs).",
        )
