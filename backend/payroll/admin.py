from django.contrib import admin

from .models import (
    SalaryStructure,
    SalaryComponent,
    SalaryStructureComponent,
    EmployeeSalary,
    PayrollCycle,
    PayrollRun,
    PayrollItem,
    Payslip,
)


# ==========================================================
# SALARY STRUCTURE ADMIN
# ==========================================================

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "effective_from",
        "effective_to",
        "is_active",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "company__company_name",
    )

    ordering = (
        "company",
        "name",
    )

    autocomplete_fields = (
        "company",
    )

# ==========================================================
# SALARY COMPONENT ADMIN
# ==========================================================

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "company",
        "component_type",
        "calculation_type",
        "default_value",
        "is_taxable",
        "is_mandatory",
        "is_active",
    )

    list_filter = (
        "company",
        "component_type",
        "calculation_type",
        "is_taxable",
        "is_mandatory",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "company__company_name",
    )

    ordering = (
        "company",
        "component_type",
        "name",
    )

    autocomplete_fields = (
        "company",
    )


# ==========================================================
# SALARY STRUCTURE COMPONENT ADMIN
# ==========================================================

@admin.register(SalaryStructureComponent)
class SalaryStructureComponentAdmin(admin.ModelAdmin):

    list_display = (
        "structure",
        "component",
        "effective_calculation_type",
        "effective_value",
        "display_order",
        "is_active",
    )

    list_filter = (
        "structure__company",
        "is_active",
        "override_calculation_type",
    )

    search_fields = (
        "structure__name",
        "component__name",
        "component__code",
    )

    ordering = (
        "structure",
        "display_order",
    )

    autocomplete_fields = (
        "structure",
        "component",
    )

# ==========================================================
# EMPLOYEE SALARY ADMIN
# ==========================================================

@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "company",
        "structure",
        "basic_salary",
        "effective_from",
        "effective_to",
        "is_active",
    )

    list_filter = (
        "company",
        "structure",
        "is_active",
    )

    search_fields = (
        "employee__employee_id",
        "employee__full_name",
        "structure__name",
        "company__company_name",
    )

    ordering = (
        "employee",
        "-effective_from",
    )

    autocomplete_fields = (
        "company",
        "employee",
        "structure",
        "created_by",
    )

    date_hierarchy = "effective_from"


# ==========================================================
# PAYROLL CYCLE ADMIN
# ==========================================================

@admin.register(PayrollCycle)
class PayrollCycleAdmin(admin.ModelAdmin):

    list_display = (
        "period_label",
        "company",
        "start_date",
        "end_date",
        "total_working_days",
        "status",
    )

    list_filter = (
        "company",
        "status",
        "year",
        "month",
    )

    search_fields = (
        "company__company_name",
    )

    ordering = (
        "-year",
        "-month",
    )

    autocomplete_fields = (
        "company",
        "created_by",
        "closed_by",
    )

    date_hierarchy = "start_date"

    readonly_fields = (
        "created_at",
        "updated_at",
        "closed_at",
    )

# ==========================================================
# PAYROLL RUN ADMIN
# ==========================================================

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):

    list_display = (
        "cycle",
        "run_number",
        "status",
        "total_employees",
        "total_gross",
        "total_deductions",
        "total_net",
        "created_by",
        "created_at",
    )

    list_filter = (
        "company",
        "status",
        "cycle__year",
        "cycle__month",
    )

    search_fields = (
        "description",
        "cycle__company__company_name",
    )

    ordering = (
        "-created_at",
    )

    autocomplete_fields = (
        "company",
        "cycle",
        "created_by",
        "approved_by",
        "finalized_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "approved_at",
        "finalized_at",
    )

    date_hierarchy = "created_at"


# ==========================================================
# PAYROLL ITEM ADMIN
# ==========================================================

@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "component_name",
        "component_type",
        "amount",
        "payroll_run",
        "display_order",
    )

    list_filter = (
        "company",
        "component_type",
        "payroll_run",
    )

    search_fields = (
        "employee__employee_id",
        "employee__full_name",
        "component_name",
    )

    ordering = (
        "employee",
        "display_order",
    )

    autocomplete_fields = (
        "company",
        "payroll_run",
        "employee",
        "component",
    )

    readonly_fields = (
        "component_name",
        "component_type",
        "calculation_type",
        "is_taxable",
        "created_at",
    ) 


# ==========================================================
# PAYSLIP ADMIN
# ==========================================================

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "payroll_run",
        "basic_salary",
        "gross_salary",
        "total_deductions",
        "net_salary",
        "status",
        "issued_at",
    )

    list_filter = (
        "company",
        "status",
        "payroll_run",
    )

    search_fields = (
        "employee__employee_id",
        "employee__full_name",
        "payroll_run__cycle__company__company_name",
    )

    ordering = (
        "-created_at",
    )

    autocomplete_fields = (
        "company",
        "payroll_run",
        "employee",
        "employee_salary",
        "issued_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "created_at"