"""
==========================================================
NexusERP-AI Report Services
==========================================================

Read-only analytics layer for NexusERP.

Philosophy:
    - Never modifies business data
    - Aggregates data from existing modules
    - AI consumes this layer, not raw module ORM
    - Every query is company-scoped
    - Every method accepts optional filters
    - Summary and trend methods included for AI/dashboards

Service Classes:
    BaseReportService           ← shared __init__
    EmployeeReportService
    LeaveReportService
    PayrollReportService
    InventoryReportService
    PaymentReportService
    AttendanceReportService

Export:
    ExportService will consume report service output.
    Report services never generate files directly.

Caching:
    Service layer is cache-ready. Add cache.get/set
    around any method without changing signatures.
==========================================================
"""

from django.db.models import (
    Avg,
    Case,
    Count,
    DecimalField,
    F,
    FloatField,
    IntegerField,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone


# ==========================================================
# BASE REPORT SERVICE
# ==========================================================

class BaseReportService:
    """
    Shared base for all report services.

    Provides:
        - Company scoping
        - Common date helpers
    """

    def __init__(self, company):
        self.company = company

    def _current_year(self):
        return timezone.now().year

    def _current_month(self):
        return timezone.now().month

    def _today(self):
        return timezone.localdate()


# ==========================================================
# EMPLOYEE REPORT SERVICE
# ==========================================================

class EmployeeReportService(BaseReportService):
    """
    Read-only analytics for the Employee module.
    """

    def _base_queryset(self):
        from employees.models import Employee
        return (
            Employee.objects
            .select_related(
                "department",
                "designation",
                "reporting_manager",
            )
            .filter(company=self.company)
        )

    # ── Summary ──────────────────────────────────────────

    def employee_summary(self):
        """
        High-level KPIs for dashboards and AI.

        Returns
        -------
        dict
            total, active, inactive, on_probation,
            new_this_month, resigned_this_month
        """
        from employees.models import Employee

        today = self._today()

        base = Employee.objects.filter(company=self.company)

        counts = base.aggregate(
            total=Count("id"),
            active=Count(
                Case(When(is_active=True, then=Value(1)),
                     output_field=IntegerField())
            ),
            inactive=Count(
                Case(When(is_active=False, then=Value(1)),
                     output_field=IntegerField())
            ),
            on_probation=Count(
                Case(When(employee_status="Probation", then=Value(1)),
                     output_field=IntegerField())
            ),
            new_this_month=Count(
                Case(
                    When(
                        joining_date__year=today.year,
                        joining_date__month=today.month,
                        then=Value(1),
                    ),
                    output_field=IntegerField(),
                )
            ),
            resigned_this_month=Count(
                Case(
                    When(
                        resignation_date__year=today.year,
                        resignation_date__month=today.month,
                        then=Value(1),
                    ),
                    output_field=IntegerField(),
                )
            ),
        )

        return counts

    # ── List Reports ─────────────────────────────────────

    def employee_register(
        self,
        is_active=True,
        department_id=None,
        designation_id=None,
        employment_type=None,
        employee_status=None,
        joining_date_from=None,
        joining_date_to=None,
    ):
        """
        Full employee list with optional filters.
        """
        qs = self._base_queryset()

        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if department_id:
            qs = qs.filter(department__id=department_id)
        if designation_id:
            qs = qs.filter(designation__id=designation_id)
        if employment_type:
            qs = qs.filter(employment_type=employment_type)
        if employee_status:
            qs = qs.filter(employee_status=employee_status)
        if joining_date_from:
            qs = qs.filter(joining_date__gte=joining_date_from)
        if joining_date_to:
            qs = qs.filter(joining_date__lte=joining_date_to)

        return qs.order_by("employee_id")

    def employees_by_department(self):
        """
        Active employee count per department.
        """
        from employees.models import Employee
        return (
            Employee.objects
            .filter(company=self.company, is_active=True)
            .values(
                "department__id",
                "department__department_name",
            )
            .annotate(employee_count=Count("id"))
            .order_by("-employee_count")
        )

    def employees_by_designation(self):
        """
        Active employee count per designation.
        """
        from employees.models import Employee
        return (
            Employee.objects
            .filter(company=self.company, is_active=True)
            .values(
                "designation__id",
                "designation__designation_name",
            )
            .annotate(employee_count=Count("id"))
            .order_by("-employee_count")
        )

    def employees_by_status(self):
        """
        Employee count per employee_status.
        """
        from employees.models import Employee
        return (
            Employee.objects
            .filter(company=self.company)
            .values("employee_status")
            .annotate(count=Count("id"))
            .order_by("employee_status")
        )

    def joining_report(
        self,
        date_from=None,
        date_to=None,
        department_id=None,
    ):
        """
        Employees who joined within a date range.
        """
        qs = self._base_queryset().filter(is_active=True)
        if date_from:
            qs = qs.filter(joining_date__gte=date_from)
        if date_to:
            qs = qs.filter(joining_date__lte=date_to)
        if department_id:
            qs = qs.filter(department__id=department_id)
        return qs.order_by("joining_date")

    def resignation_report(
        self,
        date_from=None,
        date_to=None,
        department_id=None,
    ):
        """
        Employees who resigned within a date range.
        """
        from employees.models import Employee
        qs = (
            Employee.objects
            .filter(
                company=self.company,
                resignation_date__isnull=False,
            )
            .select_related("department", "designation")
        )
        if date_from:
            qs = qs.filter(resignation_date__gte=date_from)
        if date_to:
            qs = qs.filter(resignation_date__lte=date_to)
        if department_id:
            qs = qs.filter(department__id=department_id)
        return qs.order_by("-resignation_date")

    # ── Trends ───────────────────────────────────────────

    def headcount_trend(self, year=None):
        """
        Monthly headcount change for a year.
        Shows how many employees joined each month.
        """
        from employees.models import Employee
        if year is None:
            year = self._current_year()
        return (
            Employee.objects
            .filter(
                company=self.company,
                joining_date__year=year,
            )
            .values(month=TruncMonth("joining_date"))
            .annotate(joinings=Count("id"))
            .order_by("month")
        )


# ==========================================================
# LEAVE REPORT SERVICE
# ==========================================================

class LeaveReportService(BaseReportService):
    """
    Read-only analytics for the Leave module.
    """

    def _base_queryset(self):
        from leave_management.models import LeaveRequest
        return (
            LeaveRequest.objects
            .select_related(
                "employee",
                "employee__department",
                "employee__designation",
                "leave_type",
            )
            .filter(employee__company=self.company)
        )

    # ── Summary ──────────────────────────────────────────

    def leave_summary(self, year=None):
        """
        High-level leave KPIs for dashboards and AI.
        """
        from leave_management.models import LeaveRequest
        if year is None:
            year = self._current_year()

        return (
            LeaveRequest.objects
            .filter(
                employee__company=self.company,
                start_date__year=year,
            )
            .aggregate(
                total_requests=Count("id"),
                approved=Count(
                    Case(When(approval_status="Approved", then=Value(1)),
                         output_field=IntegerField())
                ),
                pending=Count(
                    Case(When(approval_status="Pending", then=Value(1)),
                         output_field=IntegerField())
                ),
                rejected=Count(
                    Case(When(approval_status="Rejected", then=Value(1)),
                         output_field=IntegerField())
                ),
                total_days_taken=Coalesce(
                    Sum(
                        Case(
                            When(approval_status="Approved", then=F("total_days")),
                            output_field=FloatField(),
                        )
                    ),
                    Value(0),
                    output_field=FloatField(),
                ),
            )
        )

    # ── List Reports ─────────────────────────────────────

    def leave_balance_report(
        self,
        department_id=None,
        leave_type_id=None,
    ):
        """
        Current leave balance for active employees.
        """
        from leave_management.models import LeaveBalance
        qs = (
            LeaveBalance.objects
            .select_related(
                "employee",
                "employee__department",
                "leave_type",
            )
            .filter(
                employee__company=self.company,
                employee__is_active=True,
            )
        )
        if department_id:
            qs = qs.filter(employee__department__id=department_id)
        if leave_type_id:
            qs = qs.filter(leave_type__id=leave_type_id)
        return qs.order_by(
            "employee__employee_id",
            "leave_type__leave_name",
        )

    def leave_history(
        self,
        employee_id=None,
        department_id=None,
        leave_type_id=None,
        status=None,
        date_from=None,
        date_to=None,
    ):
        """
        Leave request history with optional filters.
        """
        qs = self._base_queryset()
        if employee_id:
            qs = qs.filter(employee__id=employee_id)
        if department_id:
            qs = qs.filter(employee__department__id=department_id)
        if leave_type_id:
            qs = qs.filter(leave_type__id=leave_type_id)
        if status:
            qs = qs.filter(approval_status=status)
        if date_from:
            qs = qs.filter(start_date__gte=date_from)
        if date_to:
            qs = qs.filter(end_date__lte=date_to)
        return qs.order_by("-start_date")

    def department_leave_summary(
        self,
        date_from=None,
        date_to=None,
    ):
        """
        Total approved leave days per department.
        """
        from leave_management.models import LeaveRequest
        qs = (
            LeaveRequest.objects
            .filter(
                employee__company=self.company,
                approval_status="Approved",
            )
        )
        if date_from:
            qs = qs.filter(start_date__gte=date_from)
        if date_to:
            qs = qs.filter(end_date__lte=date_to)
        return (
            qs
            .values("employee__department__department_name")
            .annotate(
                total_leave_days=Coalesce(
                    Sum("total_days"),
                    Value(0),
                    output_field=FloatField(),
                ),
                total_requests=Count("id"),
            )
            .order_by("-total_leave_days")
        )

    # ── Trends ───────────────────────────────────────────

    def leave_trend(self, year=None):
        """
        Monthly leave request counts for a year.
        Useful for AI to detect seasonal patterns.
        """
        from leave_management.models import LeaveRequest
        if year is None:
            year = self._current_year()
        return (
            LeaveRequest.objects
            .filter(
                employee__company=self.company,
                start_date__year=year,
            )
            .values(month=TruncMonth("start_date"))
            .annotate(
                request_count=Count("id"),
                total_days=Coalesce(
                    Sum("total_days"),
                    Value(0),
                    output_field=FloatField(),
                ),
            )
            .order_by("month")
        )


# ==========================================================
# PAYROLL REPORT SERVICE
# ==========================================================

class PayrollReportService(BaseReportService):
    """
    Read-only analytics for the Payroll module.
    """

    # ── Summary ──────────────────────────────────────────

    def payroll_summary(self, year=None):
        """
        High-level payroll KPIs for dashboards and AI.
        """
        from payroll.models import Payslip
        if year is None:
            year = self._current_year()
        return (
            Payslip.objects
            .filter(
                company=self.company,
                payroll_run__cycle__year=year,
            )
            .aggregate(
                total_payslips=Count("id"),
                total_gross=Coalesce(
                    Sum("gross_salary"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                total_net=Coalesce(
                    Sum("net_salary"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                total_deductions=Coalesce(
                    Sum("total_deductions"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                avg_net_salary=Coalesce(
                    Avg("net_salary"),
                    Value(0),
                    output_field=DecimalField(),
                ),
            )
        )

    # ── List Reports ─────────────────────────────────────

    def payroll_register(
        self,
        run_id=None,
        month=None,
        year=None,
        department_id=None,
    ):
        """
        Payslips with optional filters.
        """
        from payroll.models import Payslip
        qs = (
            Payslip.objects
            .select_related(
                "employee",
                "employee__department",
                "employee__designation",
                "payroll_run",
                "payroll_run__cycle",
            )
            .filter(company=self.company)
        )
        if run_id:
            qs = qs.filter(payroll_run__id=run_id)
        if month:
            qs = qs.filter(payroll_run__cycle__month=month)
        if year:
            qs = qs.filter(payroll_run__cycle__year=year)
        if department_id:
            qs = qs.filter(employee__department__id=department_id)
        return qs.order_by("employee__employee_id")

    def department_salary_cost(
        self,
        month=None,
        year=None,
    ):
        """
        Total salary cost per department.
        """
        from payroll.models import Payslip
        qs = Payslip.objects.filter(company=self.company)
        if month:
            qs = qs.filter(payroll_run__cycle__month=month)
        if year:
            qs = qs.filter(payroll_run__cycle__year=year)
        return (
            qs
            .values("employee__department__department_name")
            .annotate(
                total_gross=Coalesce(
                    Sum("gross_salary"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                total_net=Coalesce(
                    Sum("net_salary"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                total_deductions=Coalesce(
                    Sum("total_deductions"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                employee_count=Count("employee", distinct=True),
            )
            .order_by("-total_net")
        )

    # ── Trends ───────────────────────────────────────────

    def payroll_trend(self, year=None):
        """
        Month-by-month payroll cost trend.
        Valuable for AI forecasting and budget analysis.
        """
        from payroll.models import Payslip
        if year is None:
            year = self._current_year()
        return (
            Payslip.objects
            .filter(
                company=self.company,
                payroll_run__cycle__year=year,
            )
            .values(month=F("payroll_run__cycle__month"))
            .annotate(
                total_gross=Coalesce(
                    Sum("gross_salary"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                total_net=Coalesce(
                    Sum("net_salary"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                employee_count=Count("employee", distinct=True),
            )
            .order_by("month")
        )

    # ── AI Insights ──────────────────────────────────────

    def highest_earners(self, limit=10):
        """
        Top earners by net salary.
        AI can use this for compensation analysis.
        """
        from payroll.models import Payslip
        return (
            Payslip.objects
            .filter(company=self.company)
            .values(
                "employee__id",
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "employee__department__department_name",
            )
            .annotate(avg_net=Avg("net_salary"))
            .order_by("-avg_net")[:limit]
        )


# ==========================================================
# INVENTORY REPORT SERVICE
# ==========================================================

class InventoryReportService(BaseReportService):
    """
    Read-only analytics for the Inventory module.
    """

    # ── Summary ──────────────────────────────────────────

    def inventory_summary(self):
        """
        High-level asset KPIs for dashboards and AI.
        """
        from inventory.models import Asset

        return (
            Asset.objects
            .filter(company=self.company)
            .aggregate(
                total_assets=Count("id"),
                available=Count(
                    Case(When(status="Available", then=Value(1)),
                         output_field=IntegerField())
                ),
                assigned=Count(
                    Case(When(status="Assigned", then=Value(1)),
                         output_field=IntegerField())
                ),
                under_maintenance=Count(
                    Case(When(status="Maintenance", then=Value(1)),
                         output_field=IntegerField())
                ),
                retired=Count(
                    Case(When(status="Retired", then=Value(1)),
                         output_field=IntegerField())
                ),
                total_purchase_cost=Coalesce(
                    Sum("purchase_cost"),
                    Value(0),
                    output_field=DecimalField(),
                ),
            )
        )

    # ── List Reports ─────────────────────────────────────

    def asset_register(
        self,
        status=None,
        category_id=None,
        vendor_id=None,
        is_active=True,
    ):
        """
        Full asset list with optional filters.
        """
        from inventory.models import Asset
        qs = (
            Asset.objects
            .select_related("category", "vendor")
            .filter(company=self.company)
        )
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if status:
            qs = qs.filter(status=status)
        if category_id:
            qs = qs.filter(category__id=category_id)
        if vendor_id:
            qs = qs.filter(vendor__id=vendor_id)
        return qs.order_by("category__name", "asset_tag")

    def assigned_assets(
        self,
        department_id=None,
        employee_id=None,
    ):
        """
        Assets currently assigned to employees.
        """
        from inventory.models import AssetAssignment
        qs = (
            AssetAssignment.objects
            .select_related(
                "asset",
                "asset__category",
                "employee",
                "employee__department",
            )
            .filter(
                company=self.company,
                returned_date__isnull=True,
            )
        )
        if department_id:
            qs = qs.filter(employee__department__id=department_id)
        if employee_id:
            qs = qs.filter(employee__id=employee_id)
        return qs.order_by(
            "employee__employee_id",
            "asset__category__name",
        )

    def maintenance_history(
        self,
        asset_id=None,
        status=None,
        date_from=None,
        date_to=None,
    ):
        """
        Maintenance records with optional filters.
        """
        from inventory.models import AssetMaintenance
        qs = (
            AssetMaintenance.objects
            .select_related("asset", "vendor")
            .filter(company=self.company)
        )
        if asset_id:
            qs = qs.filter(asset__id=asset_id)
        if status:
            qs = qs.filter(status=status)
        if date_from:
            qs = qs.filter(scheduled_date__gte=date_from)
        if date_to:
            qs = qs.filter(scheduled_date__lte=date_to)
        return qs.order_by("-scheduled_date")

    def retired_assets(self, category_id=None):
        """
        All retired assets.
        """
        from inventory.models import Asset, AssetStatus
        qs = (
            Asset.objects
            .select_related("category", "vendor")
            .filter(
                company=self.company,
                status=AssetStatus.RETIRED,
            )
        )
        if category_id:
            qs = qs.filter(category__id=category_id)
        return qs.order_by("category__name", "asset_tag")

    # ── Trends ───────────────────────────────────────────

    def maintenance_cost_trend(self, year=None):
        """
        Monthly maintenance cost trend.
        AI can use this to detect rising repair costs.
        """
        from inventory.models import AssetMaintenance
        if year is None:
            year = self._current_year()
        return (
            AssetMaintenance.objects
            .filter(
                company=self.company,
                status="Completed",
                completed_date__year=year,
                cost__isnull=False,
            )
            .values(month=TruncMonth("completed_date"))
            .annotate(
                total_cost=Coalesce(
                    Sum("cost"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                repair_count=Count("id"),
            )
            .order_by("month")
        )

    # ── AI Insights ──────────────────────────────────────

    def most_maintained_assets(self, limit=10):
        """
        Assets with the most maintenance records.
        AI can flag these as candidates for retirement.
        """
        from inventory.models import AssetMaintenance
        return (
            AssetMaintenance.objects
            .filter(company=self.company)
            .values(
                "asset__id",
                "asset__asset_tag",
                "asset__name",
                "asset__category__name",
            )
            .annotate(maintenance_count=Count("id"))
            .order_by("-maintenance_count")[:limit]
        )

    def assets_by_vendor(self):
        """
        Asset count and total cost per vendor.
        """
        from inventory.models import Asset
        return (
            Asset.objects
            .filter(company=self.company)
            .values("vendor__id", "vendor__name")
            .annotate(
                asset_count=Count("id"),
                total_cost=Coalesce(
                    Sum("purchase_cost"),
                    Value(0),
                    output_field=DecimalField(),
                ),
            )
            .order_by("-asset_count")
        )


# ==========================================================
# PAYMENT REPORT SERVICE
# ==========================================================

class PaymentReportService(BaseReportService):
    """
    Read-only analytics for the Payments module.
    """

    def _base_queryset(self):
        from payments.models import Payment
        return (
            Payment.objects
            .select_related(
                "employee",
                "employee__department",
                "payslip",
            )
            .filter(company=self.company)
        )

    # ── Summary ──────────────────────────────────────────

    def payment_summary(self, year=None):
        """
        High-level payment KPIs for dashboards and AI.
        """
        from payments.models import PaymentStatus
        if year is None:
            year = self._current_year()

        return (
            self._base_queryset()
            .filter(created_at__year=year)
            .aggregate(
                total_payments=Count("id"),
                total_paid=Coalesce(
                    Sum(
                        Case(
                            When(
                                status=PaymentStatus.PAID,
                                then=F("amount"),
                            ),
                            output_field=DecimalField(),
                        )
                    ),
                    Value(0),
                    output_field=DecimalField(),
                ),
                pending_count=Count(
                    Case(
                        When(status=PaymentStatus.PENDING,
                             then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                failed_count=Count(
                    Case(
                        When(status=PaymentStatus.FAILED,
                             then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
                cancelled_count=Count(
                    Case(
                        When(status=PaymentStatus.CANCELLED,
                             then=Value(1)),
                        output_field=IntegerField(),
                    )
                ),
            )
        )

    # ── List Reports ─────────────────────────────────────

    def payment_register(
        self,
        status=None,
        payment_method=None,
        date_from=None,
        date_to=None,
        employee_id=None,
    ):
        """
        All payments with optional filters.
        """
        from payments.models import PaymentStatus
        qs = self._base_queryset()
        if status:
            qs = qs.filter(status=status)
        if payment_method:
            qs = qs.filter(payment_method=payment_method)
        if date_from:
            qs = qs.filter(payment_date__gte=date_from)
        if date_to:
            qs = qs.filter(payment_date__lte=date_to)
        if employee_id:
            qs = qs.filter(employee__id=employee_id)
        return qs.order_by("-created_at")

    def pending_payments(self):
        """
        Payments in Pending or Processing state.
        """
        from payments.models import PaymentStatus
        return (
            self._base_queryset()
            .filter(
                status__in=[
                    PaymentStatus.PENDING,
                    PaymentStatus.PROCESSING,
                ]
            )
            .order_by("created_at")
        )

    def failed_payments(
        self,
        date_from=None,
        date_to=None,
    ):
        """
        Failed payments with optional date filter.
        """
        from payments.models import PaymentStatus
        qs = self._base_queryset().filter(
            status=PaymentStatus.FAILED,
        )
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs.order_by("-created_at")

    # ── Trends ───────────────────────────────────────────

    def payment_trend(self, year=None):
        """
        Monthly payment volume trend.
        Paid payments only.
        """
        from payments.models import PaymentStatus
        if year is None:
            year = self._current_year()
        return (
            self._base_queryset()
            .filter(
                status=PaymentStatus.PAID,
                payment_date__year=year,
            )
            .values(month=TruncMonth("payment_date"))
            .annotate(
                total_paid=Coalesce(
                    Sum("amount"),
                    Value(0),
                    output_field=DecimalField(),
                ),
                payment_count=Count("id"),
            )
            .order_by("month")
        )

# ==========================================================
# ATTENDANCE REPORT SERVICE
# ==========================================================

class AttendanceReportService(BaseReportService):
    """
    Read-only aggregated analytics for the Attendance module.

    Complements attendance/reports.py
    ----------------------------------
    attendance/reports.py   → powers live attendance APIs
                              returns raw QuerySets
                              used by attendance/report_views.py

    This class               → powers the reports module and AI layer
                              returns aggregated dicts and counts
                              used by reports/ views and AI service

    The two are intentionally separate.
    Never merge them.
    """

    def _base_queryset(self):
        from attendance.models import Attendance
        return (
            Attendance.objects
            .select_related(
                "employee",
                "employee__department",
                "employee__designation",
                "shift",
            )
            .filter(
                employee__company=self.company,
                is_active=True,
            )
        )

    # ── Summary ──────────────────────────────────────────

    def attendance_summary(self, month=None, year=None):
        """
        High-level attendance KPIs for dashboards and AI.

        Returns
        -------
        dict
            total_records, present_count, absent_count,
            half_day_count, leave_count, late_count,
            total_working_minutes, total_overtime_minutes,
            total_late_minutes, attendance_percentage
        """
        from attendance.models import AttendanceStatus

        if year is None:
            year = self._current_year()
        if month is None:
            month = self._current_month()

        qs = self._base_queryset().filter(
            date__year=year,
            date__month=month,
        )

        return qs.aggregate(
            total_records=Count("id"),
            present_count=Count(
                Case(
                    When(
                        status=AttendanceStatus.PRESENT,
                        then=Value(1),
                    ),
                    output_field=IntegerField(),
                )
            ),
            absent_count=Count(
                Case(
                    When(
                        status=AttendanceStatus.ABSENT,
                        then=Value(1),
                    ),
                    output_field=IntegerField(),
                )
            ),
            half_day_count=Count(
                Case(
                    When(
                        status=AttendanceStatus.HALF_DAY,
                        then=Value(1),
                    ),
                    output_field=IntegerField(),
                )
            ),
            leave_count=Count(
                Case(
                    When(
                        status=AttendanceStatus.LEAVE,
                        then=Value(1),
                    ),
                    output_field=IntegerField(),
                )
            ),
            late_count=Count(
                Case(
                    When(
                        late_minutes__gt=0,
                        then=Value(1),
                    ),
                    output_field=IntegerField(),
                )
            ),
            total_working_minutes=Coalesce(
                Sum("working_minutes"),
                Value(0),
                output_field=IntegerField(),
            ),
            total_overtime_minutes=Coalesce(
                Sum("overtime_minutes"),
                Value(0),
                output_field=IntegerField(),
            ),
            total_late_minutes=Coalesce(
                Sum("late_minutes"),
                Value(0),
                output_field=IntegerField(),
            ),
        )

    # ── List Reports ─────────────────────────────────────

    def department_attendance_summary(
        self,
        month=None,
        year=None,
    ):
        """
        Attendance totals grouped by department.

        Useful for HR to compare departments at a glance.
        AI can use this to detect underperforming departments.

        Returns
        -------
        QuerySet of dicts
            department_name, present_count, absent_count,
            half_day_count, leave_count, late_count,
            total_working_minutes
        """
        from attendance.models import AttendanceStatus

        if year is None:
            year = self._current_year()
        if month is None:
            month = self._current_month()

        return (
            self._base_queryset()
            .filter(
                date__year=year,
                date__month=month,
            )
            .values(
                "employee__department__id",
                "employee__department__department_name",
            )
            .annotate(
                present_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.PRESENT,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                absent_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.ABSENT,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                half_day_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.HALF_DAY,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                leave_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.LEAVE,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                late_count=Count(
                    Case(
                        When(
                            late_minutes__gt=0,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                total_working_minutes=Coalesce(
                    Sum("working_minutes"),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )
            .order_by(
                "employee__department__department_name",
            )
        )

    def employee_attendance_summary(
        self,
        month=None,
        year=None,
        department_id=None,
    ):
        """
        Per-employee attendance totals for a month.

        Mirrors the logic in attendance/reports.py
        monthly_summary() but returns an ORM QuerySet
        instead of a Python list, making it cache-ready
        and consumable by the AI layer without re-querying.

        Returns
        -------
        QuerySet of dicts
            employee_id, employee name parts,
            department, designation,
            present_count, absent_count, half_day_count,
            leave_count, late_count,
            total_working_minutes, total_overtime_minutes,
            total_late_minutes
        """
        from attendance.models import AttendanceStatus

        if year is None:
            year = self._current_year()
        if month is None:
            month = self._current_month()

        qs = self._base_queryset().filter(
            date__year=year,
            date__month=month,
        )

        if department_id:
            qs = qs.filter(
                employee__department__id=department_id,
            )

        return (
            qs
            .values(
                "employee__id",
                "employee__employee_id",
                "employee__first_name",
                "employee__middle_name",
                "employee__last_name",
                "employee__department__department_name",
                "employee__designation__designation_name",
            )
            .annotate(
                present_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.PRESENT,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                absent_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.ABSENT,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                half_day_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.HALF_DAY,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                leave_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.LEAVE,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                late_count=Count(
                    Case(
                        When(
                            late_minutes__gt=0,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                total_working_minutes=Coalesce(
                    Sum("working_minutes"),
                    Value(0),
                    output_field=IntegerField(),
                ),
                total_overtime_minutes=Coalesce(
                    Sum("overtime_minutes"),
                    Value(0),
                    output_field=IntegerField(),
                ),
                total_late_minutes=Coalesce(
                    Sum("late_minutes"),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )
            .order_by("employee__employee_id")
        )

    # ── Trends ───────────────────────────────────────────

    def attendance_trend(self, year=None):
        """
        Month-by-month attendance counts for a year.

        AI can use this to detect seasonal absenteeism,
        festival leave patterns, or workforce health trends.

        Returns
        -------
        QuerySet of dicts
            month, present_count, absent_count,
            half_day_count, leave_count, late_count
        """
        from attendance.models import AttendanceStatus

        if year is None:
            year = self._current_year()

        return (
            self._base_queryset()
            .filter(date__year=year)
            .values(month=TruncMonth("date"))
            .annotate(
                present_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.PRESENT,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                absent_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.ABSENT,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                half_day_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.HALF_DAY,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                leave_count=Count(
                    Case(
                        When(
                            status=AttendanceStatus.LEAVE,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
                late_count=Count(
                    Case(
                        When(
                            late_minutes__gt=0,
                            then=Value(1),
                        ),
                        output_field=IntegerField(),
                    )
                ),
            )
            .order_by("month")
        )

    # ── AI Insights ──────────────────────────────────────

    def top_absentees(
        self,
        month=None,
        year=None,
        limit=10,
    ):
        """
        Employees with the highest absent days.

        AI can flag these employees for HR follow-up
        or wellness checks.

        Returns
        -------
        QuerySet of dicts
            employee_id, employee name parts,
            department, absent_days — ordered descending
        """
        from attendance.models import AttendanceStatus

        if year is None:
            year = self._current_year()
        if month is None:
            month = self._current_month()

        return (
            self._base_queryset()
            .filter(
                date__year=year,
                date__month=month,
                status=AttendanceStatus.ABSENT,
            )
            .values(
                "employee__id",
                "employee__employee_id",
                "employee__first_name",
                "employee__middle_name",
                "employee__last_name",
                "employee__department__department_name",
            )
            .annotate(absent_days=Count("id"))
            .order_by("-absent_days")[:limit]
        )

    def best_attendance(
        self,
        month=None,
        year=None,
        limit=10,
    ):
        """
        Employees with the highest present days.

        AI can use this for attendance-based recognition
        or reward programs.

        Returns
        -------
        QuerySet of dicts
            employee_id, employee name parts,
            department, present_days — ordered descending
        """
        from attendance.models import AttendanceStatus

        if year is None:
            year = self._current_year()
        if month is None:
            month = self._current_month()

        return (
            self._base_queryset()
            .filter(
                date__year=year,
                date__month=month,
                status=AttendanceStatus.PRESENT,
            )
            .values(
                "employee__id",
                "employee__employee_id",
                "employee__first_name",
                "employee__middle_name",
                "employee__last_name",
                "employee__department__department_name",
            )
            .annotate(present_days=Count("id"))
            .order_by("-present_days")[:limit]
        )