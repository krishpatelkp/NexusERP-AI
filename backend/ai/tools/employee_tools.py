"""
==========================================================
NexusERP-AI — Employee Tools
==========================================================
"""

from ai.tools.base import BaseTool, ToolContext, ToolResult
from reports.services import EmployeeReportService


# ==========================================================
# EMPLOYEE SUMMARY TOOL
# ==========================================================

class EmployeeSummaryTool(BaseTool):
    """
    Returns high-level employee statistics.

    Answers questions like:
        How many employees does my company have?
        How many are active?
        How many joined this month?
    """

    name = "employee_summary"

    description = (
        "Returns employee count, active count, inactive count, "
        "probation count, new joinings this month, and resignations "
        "this month. Use this for headcount questions."
    )

    def execute(
        self,
        context: ToolContext,
        **kwargs,
    ) -> ToolResult:

        service = EmployeeReportService(
            company=context.company,
        )

        data = service.employee_summary()

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=(
                f"Company has {data.get('total', 0)} employees "
                f"({data.get('active', 0)} active)."
            ),
        )


# ==========================================================
# EMPLOYEES BY DEPARTMENT TOOL
# ==========================================================

class EmployeesByDepartmentTool(BaseTool):
    """
    Returns employee count per department.

    Answers questions like:
        Which department has the most employees?
        How many people are in Engineering?
    """

    name = "employees_by_department"

    description = (
        "Returns the count of active employees grouped by department. "
        "Use this when the user asks about department headcount or "
        "which department has the most/least employees."
    )

    def execute(
        self,
        context: ToolContext,
        **kwargs,
    ) -> ToolResult:

        service = EmployeeReportService(
            company=context.company,
        )

        queryset = service.employees_by_department()

        data = list(queryset.values(
            "department__department_name",
            "employee_count",
        ))

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Found {len(data)} departments with employees.",
        )


# ==========================================================
# EMPLOYEE REGISTER TOOL
# ==========================================================

class EmployeeRegisterTool(BaseTool):
    """
    Returns a list of employees with optional filters.

    Answers questions like:
        List all employees in Engineering.
        Show me all contract employees.
        Who joined after January 2026?
    """

    name = "employee_register"

    description = (
        "Returns a list of employees. Supports optional filters: "
        "department_id, designation_id, employment_type, "
        "employee_status, joining_date_from, joining_date_to. "
        "Use this when the user wants to list or search employees."
    )

    def execute(
        self,
        context: ToolContext,
        department_id=None,
        designation_id=None,
        employment_type=None,
        employee_status=None,
        joining_date_from=None,
        joining_date_to=None,
        limit=10,
        **kwargs,
    ) -> ToolResult:

        service = EmployeeReportService(
            company=context.company,
        )

        queryset = service.employee_register(
            department_id=department_id,
            designation_id=designation_id,
            employment_type=employment_type,
            employee_status=employee_status,
            joining_date_from=joining_date_from,
            joining_date_to=joining_date_to,
        )

        from ai.constants import MAX_LIMIT
        limit = min(int(limit), MAX_LIMIT)

        data = list(
            queryset.values(
                "employee_id",
                "first_name",
                "last_name",
                "department__department_name",
                "designation__designation_name",
                "employment_type",
                "employee_status",
                "joining_date",
            )[:limit]
        )

        total = queryset.count()

        return ToolResult(
            success=True,
            tool=self.name,
            data={
                "total":     total,
                "shown":     len(data),
                "employees": data,
            },
            message=f"Found {total} employees (showing {len(data)}).",
        )