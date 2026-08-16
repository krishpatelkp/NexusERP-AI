"""
==========================================================
NexusERP-AI — Inventory Tools
==========================================================

AI tools for querying asset summaries, assigned assets,
and asset maintenance history.
All tools inherit from BaseTool and wrap InventoryReportService.
"""

from ai.tools.base import BaseTool, ToolContext, ToolResult
from reports.services import InventoryReportService


# ==========================================================
# INVENTORY SUMMARY TOOL
# ==========================================================

class InventorySummaryTool(BaseTool):
    """
    Returns high-level asset KPIs for the company.

    Answers questions like:
        How many assets does the company have?
        How many laptops are available?
        What is the total asset value?
    """

    name = "inventory_summary"

    description = (
        "Returns high-level asset KPIs: total assets, available count, "
        "assigned count, under maintenance count, retired count, and total purchase cost. "
        "Best for 'How many assets does the company have?' or 'How many laptops are available?' "
        "or 'What is the total asset value?'."
    )

    def execute(
        self,
        context: ToolContext,
        **kwargs,
    ) -> ToolResult:
        """
        Executes high-level asset inventory summary query.
        """
        service = InventoryReportService(
            company=context.company,
        )

        data = service.inventory_summary()

        total = data.get("total_assets", 0) if data else 0

        if not data or total == 0:
            return ToolResult(
                success=True,
                tool=self.name,
                data=data or {},
                message="No records found.",
            )

        available = data.get("available", 0)
        assigned = data.get("assigned", 0)
        total_cost = float(data.get("total_purchase_cost", 0) or 0)
        formatted_cost = f"₹{total_cost:,.2f}"

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=(
                f"Company has {total} total assets ({assigned} assigned, {available} available). "
                f"Total asset purchase cost is {formatted_cost}."
            ),
        )


# ==========================================================
# ASSIGNED ASSETS TOOL
# ==========================================================

class AssignedAssetsTool(BaseTool):
    """
    Returns all assets currently assigned to employees.

    Answers questions like:
        Which assets are assigned to employees?
        What does the Engineering team have?
        What assets does employee EMP000001 hold?
    """

    name = "assigned_assets"

    description = (
        "Returns all assets currently assigned to employees with optional filters "
        "for department and employee. Best for 'Which assets are assigned to employees?' "
        "or 'What does the Engineering team have?' or 'What assets does employee EMP000001 hold?'."
    )

    def execute(
        self,
        context: ToolContext,
        department_id=None,
        employee_id=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes currently assigned assets query.
        """
        service = InventoryReportService(
            company=context.company,
        )

        queryset = service.assigned_assets(
            department_id=department_id,
            employee_id=employee_id,
        )

        raw_records = list(
            queryset.values(
                "asset__asset_tag",
                "asset__name",
                "asset__category__name",
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "employee__department__department_name",
                "assigned_date",
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
                    "asset_tag":     item.get("asset__asset_tag"),
                    "asset_name":    item.get("asset__name"),
                    "category":      item.get("asset__category__name"),
                    "employee_id":   item.get("employee__employee_id"),
                    "employee_name": full_name,
                    "department":    item.get("employee__department__department_name"),
                    "assigned_date": item.get("assigned_date"),
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Found {len(data)} currently assigned assets.",
        )


# ==========================================================
# MAINTENANCE HISTORY TOOL
# ==========================================================

class MaintenanceHistoryTool(BaseTool):
    """
    Returns asset maintenance records.

    Answers questions like:
        Which assets are under maintenance?
        Show me completed repairs this month.
        What assets have been repaired most often?
    """

    name = "maintenance_history"

    description = (
        "Returns asset maintenance records with optional filters for asset ID, "
        "status, and date range. Best for 'Which assets are under maintenance?' "
        "or 'Show me completed repairs this month' or 'What assets have been repaired most often?'."
    )

    def execute(
        self,
        context: ToolContext,
        asset_id=None,
        status=None,
        date_from=None,
        date_to=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes asset maintenance history query.
        """
        service = InventoryReportService(
            company=context.company,
        )

        queryset = service.maintenance_history(
            asset_id=asset_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

        raw_records = list(
            queryset.values(
                "asset__asset_tag",
                "asset__name",
                "maintenance_type",
                "status",
                "scheduled_date",
                "completed_date",
                "cost",
                "vendor__name",
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
                    "asset_tag":        item.get("asset__asset_tag"),
                    "asset_name":       item.get("asset__name"),
                    "maintenance_type": item.get("maintenance_type"),
                    "status":           item.get("status"),
                    "scheduled_date":   item.get("scheduled_date"),
                    "completed_date":   item.get("completed_date"),
                    "cost":             item.get("cost"),
                    "vendor":           item.get("vendor__name"),
                }
            )

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Found {len(data)} maintenance records.",
        )
