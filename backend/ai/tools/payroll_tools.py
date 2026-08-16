"""
==========================================================
NexusERP-AI — Payroll Tools
==========================================================

AI tools for querying payroll summaries, payslip registers,
and department salary cost breakdowns.
All tools inherit from BaseTool and wrap PayrollReportService.
"""

from ai.tools.base import BaseTool, ToolContext, ToolResult
from reports.services import PayrollReportService


# ==========================================================
# PAYROLL SUMMARY TOOL
# ==========================================================

class PayrollSummaryTool(BaseTool):
    """
    Returns high-level payroll KPIs for a year.

    Answers questions like:
        What is our total payroll cost this year?
        What is the average salary?
        How much did we pay in deductions in 2026?
    """

    name = "payroll_summary"

    description = (
        "Returns high-level payroll KPIs for a year: total payslips generated, "
        "total gross salary, total net salary, total deductions, and average net salary. "
        "Best for questions like 'What is our total payroll cost this year?' or "
        "'What is the average salary?' or 'How much did we pay in deductions?'."
    )

    def execute(
        self,
        context: ToolContext,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes high-level yearly payroll summary query.
        """
        year_val = int(year) if year is not None else None

        service = PayrollReportService(
            company=context.company,
        )

        data = service.payroll_summary(year=year_val)

        total_payslips = data.get("total_payslips", 0) if data else 0

        if not data or total_payslips == 0:
            return ToolResult(
                success=True,
                tool=self.name,
                data=data or {},
                message="No records found.",
            )

        total_net = float(data.get("total_net", 0) or 0)
        total_gross = float(data.get("total_gross", 0) or 0)
        avg_net = float(data.get("avg_net_salary", 0) or 0)

        year_str = str(year_val) if year_val else "current year"
        formatted_net = f"₹{total_net:,.2f}"
        formatted_gross = f"₹{total_gross:,.2f}"
        formatted_avg = f"₹{avg_net:,.2f}"

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=(
                f"Total net payroll for {year_str} is {formatted_net} "
                f"(Gross: {formatted_gross}, Avg Net: {formatted_avg}) "
                f"across {total_payslips} payslips."
            ),
        )


# ==========================================================
# PAYROLL REGISTER TOOL
# ==========================================================

class PayrollRegisterTool(BaseTool):
    """
    Returns a list of payslips with optional filters.

    Answers questions like:
        Show me payslips for June 2026.
        List payroll for the Engineering department.
        Show payslip details for run ID 5.
    """

    name = "payroll_register"

    description = (
        "Returns a list of payslips with optional filters for month, year, "
        "payroll run ID, and department. Best for 'Show me payslips for June 2026' "
        "or 'List payroll for the Engineering department'."
    )

    def execute(
        self,
        context: ToolContext,
        run_id=None,
        month=None,
        year=None,
        department_id=None,
        limit=20,
        **kwargs,
    ) -> ToolResult:
        """
        Executes payslip register query with filters.
        """
        service = PayrollReportService(
            company=context.company,
        )

        queryset = service.payroll_register(
            run_id=run_id,
            month=month,
            year=year,
            department_id=department_id,
        )

        max_limit = min(int(limit), 100) if limit else 20

        raw_records = list(
            queryset.values(
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "employee__department__department_name",
                "gross_salary",
                "net_salary",
                "total_deductions",
            )[:max_limit]
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
                    "employee_id":     item.get("employee__employee_id"),
                    "first_name":      item.get("employee__first_name"),
                    "last_name":       item.get("employee__last_name"),
                    "department":      item.get("employee__department__department_name"),
                    "gross_salary":    item.get("gross_salary"),
                    "net_salary":      item.get("net_salary"),
                    "total_deductions": item.get("total_deductions"),
                }
            )

        period_parts = []
        if month:
            period_parts.append(f"month {month}")
        if year:
            period_parts.append(f"year {year}")
        period_str = " ".join(period_parts) if period_parts else "selected criteria"

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Returned {len(data)} payslips for {period_str}.",
        )


# ==========================================================
# DEPARTMENT SALARY COST TOOL
# ==========================================================

class DepartmentSalaryCostTool(BaseTool):
    """
    Returns total salary cost broken down by department.

    Answers questions like:
        Which department costs the most in salary?
        Compare department payroll costs for June 2026.
        What is the total department salary breakdown?
    """

    name = "department_salary_cost"

    description = (
        "Returns total salary cost broken down by department with optional "
        "month and year filters. Best for 'Which department costs the most in salary?' "
        "or 'Compare department payroll costs for June 2026'."
    )

    def execute(
        self,
        context: ToolContext,
        month=None,
        year=None,
        **kwargs,
    ) -> ToolResult:
        """
        Executes department salary cost breakdown query.
        """
        service = PayrollReportService(
            company=context.company,
        )

        queryset = service.department_salary_cost(
            month=month,
            year=year,
        )

        raw_records = list(
            queryset.values(
                "employee__department__department_name",
                "total_gross",
                "total_net",
                "total_deductions",
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
                    "department":       item.get("employee__department__department_name"),
                    "total_gross":      item.get("total_gross"),
                    "total_net":        item.get("total_net"),
                    "total_deductions": item.get("total_deductions"),
                    "employee_count":   item.get("employee_count"),
                }
            )

        if month and year:
            period_str = f"for {month}/{year}"
        elif month:
            period_str = f"for month {month}"
        elif year:
            period_str = f"for year {year}"
        else:
            period_str = "all time"

        return ToolResult(
            success=True,
            tool=self.name,
            data=data,
            message=f"Returned salary cost breakdown for {len(data)} departments ({period_str}).",
        )
