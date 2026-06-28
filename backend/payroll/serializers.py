from rest_framework import serializers
from .models import (
    EmployeeSalary,
    PayrollCycle,
    PayrollItem,
    PayrollRun,
    Payslip,
    SalaryComponent,
    SalaryStructure,
    SalaryStructureComponent,
)


# ==========================================================
# PAYROLL CYCLE SERIALIZER
# ==========================================================

class PayrollCycleSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for PayrollCycle.

    Includes the human-readable period_label
    and computed state properties.
    """

    period_label = serializers.CharField(
        read_only=True,
    )

    is_closed = serializers.BooleanField(
        read_only=True,
    )

    is_editable = serializers.BooleanField(
        read_only=True,
    )

    class Meta:

        model = PayrollCycle

        fields = (
            "id",
            "company",
            "month",
            "year",
            "period_label",
            "start_date",
            "end_date",
            "total_working_days",
            "status",
            "is_closed",
            "is_editable",
            "remarks",
            "created_by",
            "closed_by",
            "closed_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


# ==========================================================
# CREATE PAYROLL CYCLE SERIALIZER
# ==========================================================

class CreatePayrollCycleSerializer(
    serializers.Serializer,
):
    """
    Accepts input for creating a payroll cycle.

    Business validation is handled by PayrollService.
    """

    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
    )

    year = serializers.IntegerField(
        min_value=2000,
        max_value=2100,
    )

    start_date = serializers.DateField()

    end_date = serializers.DateField()

    total_working_days = serializers.IntegerField(
        min_value=1,
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def validate(self, attrs):

        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError(
                {
                    "end_date":
                    "End date cannot be earlier "
                    "than start date."
                }
            )

        return attrs


# ==========================================================
# PAYROLL RUN SERIALIZER
# ==========================================================

class PayrollRunSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for PayrollRun.

    Shows cycle label, status, totals,
    and audit fields.
    """

    cycle_label = serializers.CharField(
        source="cycle.period_label",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()

    approved_by_name = serializers.SerializerMethodField()

    finalized_by_name = serializers.SerializerMethodField()

    def get_created_by_name(self, obj):
        if obj.created_by is None:
            return None
        return obj.created_by.username

    def get_approved_by_name(self, obj):
        if obj.approved_by is None:
            return None
        return obj.approved_by.username

    def get_finalized_by_name(self, obj):
        if obj.finalized_by is None:
            return None
        return obj.finalized_by.username

    class Meta:

        model = PayrollRun

        fields = (
            "id",
            "company",
            "cycle",
            "cycle_label",
            "run_number",
            "description",
            "status",
            "total_employees",
            "total_gross",
            "total_deductions",
            "total_net",
            "created_by",
            "created_by_name",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "finalized_by",
            "finalized_by_name",
            "finalized_at",
            "remarks",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields


# ==========================================================
# CREATE PAYROLL RUN SERIALIZER
# ==========================================================

class CreatePayrollRunSerializer(
    serializers.Serializer,
):
    """
    Accepts input for creating a payroll run.
    """

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# REMARKS SERIALIZER
# (used for approve / finalize / cancel)
# ==========================================================

class RemarksSerializer(
    serializers.Serializer,
):
    """
    Generic serializer for actions that
    only need an optional remarks field.

    Used by:
        - approve_payroll_run
        - finalize_payroll_run
        - cancel_payroll_run
    """

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# PAYROLL ITEM SERIALIZER
# ==========================================================

class PayrollItemSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for PayrollItem.

    Shows all snapshot fields alongside
    the computed amount.
    """

    employee_id = serializers.CharField(
        source="employee.employee_id",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    class Meta:

        model = PayrollItem

        fields = (
            "id",
            "employee_id",
            "employee_name",
            "component_name",
            "component_type",
            "calculation_type",
            "is_taxable",
            "base_amount",
            "rate",
            "amount",
            "display_order",
            "created_at",
        )

        read_only_fields = fields


# ==========================================================
# PAYSLIP SERIALIZER
# ==========================================================

class PayslipSerializer(
    serializers.ModelSerializer,
):
    """
    Read serializer for Payslip.

    Includes employee info, salary summary,
    attendance summary, and status.
    """

    employee_id = serializers.CharField(
        source="employee.employee_id",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    cycle_label = serializers.CharField(
        source="payroll_run.cycle.period_label",
        read_only=True,
    )

    issued_by_name = serializers.SerializerMethodField()

    def get_issued_by_name(self, obj):
        if obj.issued_by is None:
            return None
        return obj.issued_by.username

    class Meta:

        model = Payslip

        fields = (
            "id",
            "employee_id",
            "employee_name",
            "payroll_run",
            "cycle_label",
            "basic_salary",
            "gross_salary",
            "total_deductions",
            "net_salary",
            "period_start",
            "period_end",
            "working_days",
            "present_days",
            "paid_leave_days",
            "loss_of_pay_days",
            "status",
            "issued_by",
            "issued_by_name",
            "issued_at",
            "remarks",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields