from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    CalculationType,
    ComponentType,
    EmployeeSalary,
    PayrollCycle,
    PayrollCycleStatus,
    PayrollItem,
    PayrollRun,
    PayrollRunStatus,
    Payslip,
    PayslipStatus,
    SalaryStructureComponent,
)


# ==========================================================
# PAYROLL SERVICE
# ==========================================================

class PayrollService:
    """
    Handles all payroll business logic.

    Responsibilities
    ----------------
    - Payroll cycle management
    - Payroll run lifecycle
    - Salary calculations
    - Payroll item generation
    - Payslip generation

    Usage
    -----
    service = PayrollService(
        company=company,
        user=request.user,
    )
    cycle = service.create_payroll_cycle(
        month=6,
        year=2026,
        ...
    )
    """

    def __init__(
        self,
        *,
        company,
        user,
    ):
        self.company = company
        self.user = user

    # ======================================================
    # PHASE 1 — CREATE PAYROLL CYCLE
    # ======================================================

    def create_payroll_cycle(
        self,
        *,
        month,
        year,
        start_date,
        end_date,
        total_working_days,
        remarks="",
    ):
        """
        Create a new payroll cycle for a month/year.

        Validates:
        - Month between 1 and 12
        - Year between 2000 and 2100
        - No duplicate cycle for same company/month/year
        - end_date >= start_date
        - total_working_days > 0

        Returns the created PayrollCycle instance.
        """

        # --------------------------------------------------
        # VALIDATIONS
        # --------------------------------------------------

        if not 1 <= month <= 12:
            raise ValidationError(
                "Month must be between 1 and 12."
            )

        if not 2000 <= year <= 2100:
            raise ValidationError(
                "Year must be between 2000 and 2100."
            )

        if end_date < start_date:
            raise ValidationError(
                "End date cannot be earlier than start date."
            )

        if total_working_days <= 0:
            raise ValidationError(
                "Total working days must be greater than zero."
            )

        # Duplicate check
        duplicate = PayrollCycle.objects.filter(
            company=self.company,
            month=month,
            year=year,
        ).exists()

        if duplicate:
            raise ValidationError(
                f"A payroll cycle for "
                f"{month}/{year} already exists "
                f"for this company."
            )

        # --------------------------------------------------
        # CREATE
        # --------------------------------------------------

        cycle = PayrollCycle.objects.create(
            company=self.company,
            month=month,
            year=year,
            start_date=start_date,
            end_date=end_date,
            total_working_days=total_working_days,
            remarks=remarks,
            status=PayrollCycleStatus.DRAFT,
            created_by=self.user,
        )

        return cycle

    # ======================================================
    # PHASE 2 — ACTIVATE PAYROLL CYCLE
    # ======================================================

    def activate_payroll_cycle(
        self,
        *,
        cycle,
    ):
        """
        Move a cycle from Draft → Active.

        Only Draft cycles can be activated.
        Active cycles allow PayrollRun creation.

        Returns the updated PayrollCycle.
        """

        # --------------------------------------------------
        # VALIDATIONS
        # --------------------------------------------------

        if cycle.company != self.company:
            raise ValidationError(
                "Payroll cycle does not belong "
                "to this company."
            )

        if cycle.status != PayrollCycleStatus.DRAFT:
            raise ValidationError(
                f"Only Draft cycles can be activated. "
                f"Current status: {cycle.status}."
            )

        # --------------------------------------------------
        # UPDATE
        # --------------------------------------------------

        cycle.status = PayrollCycleStatus.ACTIVE
        cycle.save()

        return cycle

    # ======================================================
    # PHASE 3 — CREATE PAYROLL RUN
    # ======================================================

    def create_payroll_run(
        self,
        *,
        cycle,
        description="",
        remarks="",
    ):
        """
        Create a new PayrollRun inside an Active cycle.

        Auto-assigns the next run_number for the cycle.
        Only Active cycles can receive new runs.

        Returns the created PayrollRun.
        """

        # --------------------------------------------------
        # VALIDATIONS
        # --------------------------------------------------

        if cycle.company != self.company:
            raise ValidationError(
                "Payroll cycle does not belong "
                "to this company."
            )

        if cycle.status != PayrollCycleStatus.ACTIVE:
            raise ValidationError(
                f"Payroll runs can only be created "
                f"for Active cycles. "
                f"Current status: {cycle.status}."
            )

        # --------------------------------------------------
        # AUTO RUN NUMBER
        # --------------------------------------------------

        last_run = (
            PayrollRun.objects
            .filter(cycle=cycle)
            .order_by("-run_number")
            .first()
        )

        run_number = (
            last_run.run_number + 1
            if last_run else 1
        )

        # --------------------------------------------------
        # CREATE
        # --------------------------------------------------

        payroll_run = PayrollRun.objects.create(
            company=self.company,
            cycle=cycle,
            run_number=run_number,
            description=description,
            remarks=remarks,
            status=PayrollRunStatus.DRAFT,
            created_by=self.user,
        )

        return payroll_run

    # ======================================================
    # PHASE 4 — PROCESS PAYROLL RUN
    # ======================================================

    @transaction.atomic
    def process_payroll_run(
        self,
        *,
        payroll_run,
    ):
        """
        The heart of the payroll engine.

        For every active employee of the company:
            1. Find their active EmployeeSalary
            2. Read the SalaryStructure
            3. Read all SalaryStructureComponents
            4. Calculate every earning
            5. Calculate every deduction
            6. Create PayrollItems
            7. Calculate Gross, Deductions, Net
            8. Create Payslip
            9. Update PayrollRun totals

        Everything runs inside a single DB transaction.
        Any failure rolls back all changes.

        Moves run status: Draft → Processing → Processed.

        Returns the updated PayrollRun.
        """

        # --------------------------------------------------
        # VALIDATIONS
        # --------------------------------------------------

        if payroll_run.company != self.company:
            raise ValidationError(
                "Payroll run does not belong "
                "to this company."
            )

        if payroll_run.status != PayrollRunStatus.DRAFT:
            raise ValidationError(
                f"Only Draft payroll runs can be processed. "
                f"Current status: {payroll_run.status}."
            )

        cycle = payroll_run.cycle

        if cycle.status != PayrollCycleStatus.ACTIVE:
            raise ValidationError(
                "Payroll run's cycle is not Active."
            )

        # --------------------------------------------------
        # MARK AS PROCESSING
        # --------------------------------------------------

        payroll_run.status = PayrollRunStatus.PROCESSING
        payroll_run.save()

        # --------------------------------------------------
        # GET ALL ACTIVE EMPLOYEES
        # --------------------------------------------------

        from employees.models import Employee

        employees = Employee.objects.filter(
            company=self.company,
            is_active=True,
        ).select_related("company")

        if not employees.exists():
            raise ValidationError(
                "No active employees found "
                "for this company."
            )

        # --------------------------------------------------
        # ACCUMULATORS FOR RUN TOTALS
        # --------------------------------------------------

        total_employees   = 0
        total_gross_sum   = Decimal("0.00")
        total_deduct_sum  = Decimal("0.00")
        total_net_sum     = Decimal("0.00")

        # --------------------------------------------------
        # PROCESS EACH EMPLOYEE
        # --------------------------------------------------

        for employee in employees:

            # Find active salary record
            employee_salary = (
                EmployeeSalary.objects
                .filter(
                    employee=employee,
                    company=self.company,
                    is_active=True,
                )
                .select_related("structure")
                .order_by("-effective_from")
                .first()
            )

            if not employee_salary:
                # Skip employees without salary record
                continue

            basic_salary = employee_salary.basic_salary
            structure = employee_salary.structure

            # Get all active structure components
            # ordered by display_order
            structure_components = (
                SalaryStructureComponent.objects
                .filter(
                    structure=structure,
                    is_active=True,
                )
                .select_related("component")
                .order_by("display_order")
            )

            if not structure_components.exists():
                # Skip employees whose structure has
                # no components configured
                continue

            # ------------------------------------------
            # CALCULATE EACH COMPONENT
            # ------------------------------------------

            gross_salary     = Decimal("0.00")
            total_deductions = Decimal("0.00")
            payroll_items    = []

            for order, sc in enumerate(
                structure_components,
                start=1,
            ):

                component    = sc.component
                calc_type    = sc.effective_calculation_type
                rate         = sc.effective_value

                # Calculate amount
                if calc_type == CalculationType.FIXED:
                    amount = Decimal(str(rate))

                else:
                    # Percentage of basic salary
                    amount = (
                        basic_salary
                        * Decimal(str(rate))
                        / Decimal("100")
                    ).quantize(Decimal("0.01"))

                # Accumulate earnings / deductions
                if component.component_type == ComponentType.EARNING:
                    gross_salary += amount
                else:
                    total_deductions += amount

                payroll_items.append(
                    PayrollItem(
                        company=self.company,
                        payroll_run=payroll_run,
                        employee=employee,
                        component=component,
                        component_name=component.name,
                        component_type=component.component_type,
                        calculation_type=calc_type,
                        is_taxable=component.is_taxable,
                        base_amount=basic_salary,
                        rate=rate,
                        amount=amount,
                        display_order=sc.display_order or order,
                    )
                )

            # ------------------------------------------
            # BULK CREATE PAYROLL ITEMS
            # ------------------------------------------

            PayrollItem.objects.bulk_create(
                payroll_items,
                ignore_conflicts=False,
            )

            # ------------------------------------------
            # NET SALARY
            # ------------------------------------------

            net_salary = gross_salary - total_deductions

            # ------------------------------------------
            # CREATE PAYSLIP
            # ------------------------------------------

            Payslip.objects.create(
                company=self.company,
                payroll_run=payroll_run,
                employee=employee,
                employee_salary=employee_salary,
                basic_salary=basic_salary,
                gross_salary=gross_salary,
                total_deductions=total_deductions,
                net_salary=net_salary,
                period_start=cycle.start_date,
                period_end=cycle.end_date,
                working_days=cycle.total_working_days,
                present_days=cycle.total_working_days,
                paid_leave_days=Decimal("0.0"),
                loss_of_pay_days=Decimal("0.0"),
                status=PayslipStatus.GENERATED,
            )

            # ------------------------------------------
            # ACCUMULATE RUN TOTALS
            # ------------------------------------------

            total_employees  += 1
            total_gross_sum  += gross_salary
            total_deduct_sum += total_deductions
            total_net_sum    += net_salary

        # --------------------------------------------------
        # GUARD — nothing was processed
        # --------------------------------------------------

        if total_employees == 0:
            raise ValidationError(
                "No employees with active salary records "
                "were found. Payroll not processed."
            )

        # --------------------------------------------------
        # UPDATE RUN TOTALS + STATUS
        # --------------------------------------------------

        payroll_run.status            = PayrollRunStatus.PROCESSED
        payroll_run.total_employees   = total_employees
        payroll_run.total_gross       = total_gross_sum
        payroll_run.total_deductions  = total_deduct_sum
        payroll_run.total_net         = total_net_sum
        payroll_run.save()

        return payroll_run

    # ======================================================
    # PHASE 5 — APPROVE PAYROLL RUN
    # ======================================================

    def approve_payroll_run(
        self,
        *,
        payroll_run,
        remarks="",
    ):
        """
        Move a PayrollRun from Processed → Approved.

        Only Processed runs can be approved.

        Returns the updated PayrollRun.
        """

        # --------------------------------------------------
        # VALIDATIONS
        # --------------------------------------------------

        if payroll_run.company != self.company:
            raise ValidationError(
                "Payroll run does not belong "
                "to this company."
            )

        if payroll_run.status != PayrollRunStatus.PROCESSED:
            raise ValidationError(
                f"Only Processed payroll runs can be approved. "
                f"Current status: {payroll_run.status}."
            )

        # --------------------------------------------------
        # UPDATE
        # --------------------------------------------------

        payroll_run.status      = PayrollRunStatus.APPROVED
        payroll_run.approved_by = self.user
        payroll_run.approved_at = timezone.now()

        if remarks:
            payroll_run.remarks = remarks

        payroll_run.save()

        return payroll_run

    # ======================================================
    # PHASE 6 — FINALIZE PAYROLL RUN
    # ======================================================

    @transaction.atomic
    def finalize_payroll_run(
        self,
        *,
        payroll_run,
        remarks="",
    ):
        """
        Move a PayrollRun from Approved → Finalized.
        Issue all Payslips in this run.

        Only Approved runs can be finalized.
        Once Finalized, nothing can be changed.

        Returns the updated PayrollRun.
        """

        # --------------------------------------------------
        # VALIDATIONS
        # --------------------------------------------------

        if payroll_run.company != self.company:
            raise ValidationError(
                "Payroll run does not belong "
                "to this company."
            )

        if payroll_run.status != PayrollRunStatus.APPROVED:
            raise ValidationError(
                f"Only Approved payroll runs can be finalized. "
                f"Current status: {payroll_run.status}."
            )

        # --------------------------------------------------
        # ISSUE ALL PAYSLIPS
        # --------------------------------------------------

        now = timezone.now()

        Payslip.objects.filter(
            payroll_run=payroll_run,
            status=PayslipStatus.GENERATED,
        ).update(
            status=PayslipStatus.ISSUED,
            issued_by=self.user,
            issued_at=now,
        )

        # --------------------------------------------------
        # FINALIZE THE RUN
        # --------------------------------------------------

        payroll_run.status       = PayrollRunStatus.FINALIZED
        payroll_run.finalized_by = self.user
        payroll_run.finalized_at = now

        if remarks:
            payroll_run.remarks = remarks

        payroll_run.save()

        return payroll_run

    # ======================================================
    # PHASE 7 — CANCEL PAYROLL RUN
    # ======================================================

    @transaction.atomic
    def cancel_payroll_run(
        self,
        *,
        payroll_run,
        remarks="",
    ):
        """
        Cancel a PayrollRun.

        Can cancel runs in any status EXCEPT Finalized.
        Deletes all PayrollItems and Payslips
        associated with this run.

        Returns the updated PayrollRun.
        """

        # --------------------------------------------------
        # VALIDATIONS
        # --------------------------------------------------

        if payroll_run.company != self.company:
            raise ValidationError(
                "Payroll run does not belong "
                "to this company."
            )

        if payroll_run.status == PayrollRunStatus.FINALIZED:
            raise ValidationError(
                "Finalized payroll runs cannot be cancelled."
            )

        # --------------------------------------------------
        # DELETE ALL GENERATED DATA
        # --------------------------------------------------

        Payslip.objects.filter(
            payroll_run=payroll_run,
        ).delete()

        PayrollItem.objects.filter(
            payroll_run=payroll_run,
        ).delete()

        # --------------------------------------------------
        # CANCEL THE RUN
        # --------------------------------------------------

        payroll_run.status = PayrollRunStatus.CANCELLED

        if remarks:
            payroll_run.remarks = remarks

        payroll_run.save()

        return payroll_run
    

    