from django.core.exceptions import ValidationError
from django.db import models

from company.models import Company


# ==========================================================
# SALARY STRUCTURE
# ==========================================================

class SalaryStructure(models.Model):
    """
    Defines a named salary structure for a company.

    A salary structure is a template that groups
    salary components together. Multiple structures
    can exist per company.

    Examples:
        Junior Engineer Structure
        Senior Engineer Structure
        Management Structure
        Contractual Structure

    This model does NOT contain employee-specific
    salary amounts. Those belong in EmployeeSalary.

    Companies can define their own structures and
    assign different structures to different employees
    or employee groups.

    Immutability:
        Structures can be deactivated but not deleted.
        Payroll history references the structure name
        via snapshot fields on PayrollItem and Payslip.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="salary_structures",
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    effective_from = models.DateField()

    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Leave blank if the structure "
            "is currently active with no end date."
        ),
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "company",
            "name",
        ]

        verbose_name = "Salary Structure"

        verbose_name_plural = "Salary Structures"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "company",
                    "name",
                ],
                name="unique_salary_structure_per_company",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["is_active"],
            ),

            models.Index(
                fields=["effective_from"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.name is not None:
            self.name = self.name.strip()

        if self.description is not None:
            self.description = self.description.strip()

        if not self.name:
            raise ValidationError(
                {
                    "name":
                    "Salary structure name is required."
                }
            )

        if (
            self.effective_to
            and self.effective_from
            and self.effective_to < self.effective_from
        ):
            raise ValidationError(
                {
                    "effective_to":
                    (
                        "Effective to date cannot be "
                        "earlier than effective from date."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.name:
            self.name = self.name.strip()

        if self.description:
            self.description = self.description.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.company.company_name}"
            f" - "
            f"{self.name}"
        )
    

# ==========================================================
# SALARY COMPONENT TYPE
# ==========================================================

class ComponentType(models.TextChoices):
    EARNING   = "Earning",   "Earning"
    DEDUCTION = "Deduction", "Deduction"


# ==========================================================
# CALCULATION TYPE
# ==========================================================

class CalculationType(models.TextChoices):
    FIXED      = "Fixed",      "Fixed Amount"
    PERCENTAGE = "Percentage", "Percentage of Basic"


# ==========================================================
# SALARY COMPONENT
# ==========================================================

class SalaryComponent(models.Model):
    """
    Represents a single salary component.

    Components are either earnings or deductions.
    They can be calculated as a fixed amount
    or as a percentage of basic salary.

    Examples:
        Earning  — Basic, HRA, DA, Special Allowance
        Deduction — PF, ESI, Professional Tax, TDS

    Design:
        Components are company-specific.
        Each company defines its own components.
        A seed command provides standard Indian
        payroll components as a starting template.

        Components are never hardcoded in Python.
        HR can add, edit, or deactivate any component.

    Immutability:
        Components can be deactivated but not deleted.
        Payroll history snapshots component names
        and amounts at the time of payroll generation.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="salary_components",
    )

    name = models.CharField(
        max_length=150,
        help_text="e.g. Basic Salary, HRA, PF",
    )

    code = models.CharField(
        max_length=20,
        help_text="e.g. BASIC, HRA, PF",
    )

    component_type = models.CharField(
        max_length=20,
        choices=ComponentType.choices,
        help_text="Earning or Deduction",
    )

    calculation_type = models.CharField(
        max_length=20,
        choices=CalculationType.choices,
        default=CalculationType.FIXED,
        help_text=(
            "Fixed: a flat amount. "
            "Percentage: % of basic salary."
        ),
    )

    default_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text=(
            "Default amount or percentage. "
            "Can be overridden per employee."
        ),
    )

    is_taxable = models.BooleanField(
        default=False,
        help_text=(
            "If True, this component is "
            "included in taxable income."
        ),
    )

    is_mandatory = models.BooleanField(
        default=False,
        help_text=(
            "If True, this component is always "
            "included in every payslip and cannot "
            "be removed per employee."
        ),
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "company",
            "component_type",
            "name",
        ]

        verbose_name = "Salary Component"

        verbose_name_plural = "Salary Components"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "company",
                    "name",
                ],
                name="unique_component_name_per_company",
            ),

            models.UniqueConstraint(
                fields=[
                    "company",
                    "code",
                ],
                name="unique_component_code_per_company",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["component_type"],
            ),

            models.Index(
                fields=["is_active"],
            ),

            models.Index(
                fields=["is_mandatory"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.name is not None:
            self.name = self.name.strip()

        if self.code is not None:
            self.code = self.code.strip().upper()

        if self.description is not None:
            self.description = self.description.strip()

        if not self.name:
            raise ValidationError(
                {
                    "name":
                    "Component name is required."
                }
            )

        if not self.code:
            raise ValidationError(
                {
                    "code":
                    "Component code is required."
                }
            )

        if self.default_value < 0:
            raise ValidationError(
                {
                    "default_value":
                    "Default value cannot be negative."
                }
            )

        if (
            self.calculation_type == CalculationType.PERCENTAGE
            and self.default_value > 100
        ):
            raise ValidationError(
                {
                    "default_value":
                    (
                        "Percentage value cannot "
                        "exceed 100."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.name:
            self.name = self.name.strip()

        if self.code:
            self.code = self.code.strip().upper()

        if self.description:
            self.description = self.description.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.company.company_name}"
            f" - "
            f"{self.name}"
            f" ({self.component_type})"
        )
    

# ==========================================================
# SALARY STRUCTURE COMPONENT
# ==========================================================

class SalaryStructureComponent(models.Model):
    """
    Maps a SalaryComponent to a SalaryStructure.

    This is the through table between
    SalaryStructure and SalaryComponent.

    Why a separate model and not ManyToManyField?

        Because the relationship carries extra data:
        - Override value per structure
        - Override calculation type per structure
        - Order of appearance on payslip
        - Whether it is active in this structure

    Example:
        Junior Engineer Structure
            Basic           Fixed    ₹25,000
            HRA             50%      of Basic
            PF              12%      of Basic
            Professional Tax Fixed   ₹200

        Senior Engineer Structure
            Basic           Fixed    ₹50,000
            HRA             50%      of Basic
            Special Allow   Fixed    ₹5,000
            PF              12%      of Basic

    The same component (HRA) can appear in multiple
    structures with different values.

    Immutability:
        Once a payroll run uses this structure,
        values are snapshotted on PayrollItem.
        Changes here do not affect past payslips.
    """

    structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.CASCADE,
        related_name="structure_components",
    )

    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        related_name="structure_components",
        help_text=(
            "Cannot delete a component that "
            "is assigned to a structure."
        ),
    )

    # ──────────────────────────────────────
    # OVERRIDE VALUES
    # ──────────────────────────────────────

    override_calculation_type = models.CharField(
        max_length=20,
        choices=CalculationType.choices,
        null=True,
        blank=True,
        help_text=(
            "If set, overrides the component's "
            "default calculation type for this "
            "structure only."
        ),
    )

    override_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text=(
            "If set, overrides the component's "
            "default value for this structure only."
        ),
    )

    # ──────────────────────────────────────
    # DISPLAY ORDER
    # ──────────────────────────────────────

    display_order = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Controls the order in which this "
            "component appears on the payslip."
        ),
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "structure",
            "display_order",
            "component",
        ]

        verbose_name = "Salary Structure Component"

        verbose_name_plural = "Salary Structure Components"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "structure",
                    "component",
                ],
                name="unique_component_per_structure",
            ),

        ]

        indexes = [

            models.Index(
                fields=["structure"],
            ),

            models.Index(
                fields=["component"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        # Component must belong to same company
        # as the structure
        if (
            self.component
            and self.structure
            and self.component.company != self.structure.company
        ):
            raise ValidationError(
                {
                    "component":
                    (
                        "Component does not belong "
                        "to the same company as "
                        "the salary structure."
                    )
                }
            )

        # Override value cannot be negative
        if (
            self.override_value is not None
            and self.override_value < 0
        ):
            raise ValidationError(
                {
                    "override_value":
                    "Override value cannot be negative."
                }
            )

        # If override calculation type is percentage,
        # override value cannot exceed 100
        effective_calc_type = (
            self.override_calculation_type
            or self.component.calculation_type
            if self.component else None
        )

        if (
            effective_calc_type == CalculationType.PERCENTAGE
            and self.override_value is not None
            and self.override_value > 100
        ):
            raise ValidationError(
                {
                    "override_value":
                    (
                        "Percentage override value "
                        "cannot exceed 100."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def effective_calculation_type(self):
        """
        Returns the calculation type that will
        actually be used during payroll generation.

        Override takes priority over component default.
        """
        return (
            self.override_calculation_type
            or self.component.calculation_type
        )

    @property
    def effective_value(self):
        """
        Returns the value that will actually be
        used during payroll generation.

        Override takes priority over component default.
        """
        if self.override_value is not None:
            return self.override_value
        return self.component.default_value

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.structure.name}"
            f" → "
            f"{self.component.name}"
        )
    


# ==========================================================
# EMPLOYEE SALARY
# ==========================================================

class EmployeeSalary(models.Model):
    """
    Stores the current salary assignment for an employee.

    Links an employee to a salary structure and records
    their actual salary amounts.

    Design decisions:
        - One active salary record per employee at a time.
        - When salary changes, a new record is created
          with a new effective_from date.
        - Old records are never deleted or overwritten.
        - This preserves complete salary history.

    Why not store salary on the Employee model?
        Because salary changes over time.
        An employee promoted in July should have
        different salary for Jan-June vs July onwards.
        Storing it here allows full salary history.

    Immutability:
        Once a PayrollRun uses this record,
        the actual amounts are snapshotted on
        PayrollItem. Changes here do not affect
        past payslips.

    Integration:
        Payroll reads this to determine which
        structure and base salary to use.
        Attendance feeds working days.
        Leave feeds leave days taken.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employee_salaries",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="salary_records",
    )

    structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.PROTECT,
        related_name="employee_salaries",
        help_text=(
            "The salary structure assigned "
            "to this employee."
        ),
    )

    # ──────────────────────────────────────
    # SALARY AMOUNTS
    # ──────────────────────────────────────

    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=(
            "The employee's basic salary. "
            "Percentage-based components are "
            "calculated from this value."
        ),
    )


    # ──────────────────────────────────────
    # EFFECTIVE PERIOD
    # ──────────────────────────────────────

    effective_from = models.DateField(
        help_text=(
            "The date from which this salary "
            "record is effective."
        ),
    )

    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "The date until which this salary "
            "record is effective. "
            "Leave blank for the current record."
        ),
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    remarks = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Reason for this salary record. "
            "e.g. Joining, Annual Increment, "
            "Promotion, Revision."
        ),
    )

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_salary_records",
    )

    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Only one active salary record "
            "should exist per employee at a time."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "employee",
            "-effective_from",
        ]

        verbose_name = "Employee Salary"

        verbose_name_plural = "Employee Salaries"

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["structure"],
            ),

            models.Index(
                fields=["effective_from"],
            ),

            models.Index(
                fields=["is_active"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.remarks is not None:
            self.remarks = self.remarks.strip()

        # Basic salary must be positive
        if (
            self.basic_salary is not None
            and self.basic_salary <= 0
        ):
            raise ValidationError(
                {
                    "basic_salary":
                    "Basic salary must be greater than zero."
                }
            )

        # effective_to cannot be before effective_from
        if (
            self.effective_to
            and self.effective_from
            and self.effective_to < self.effective_from
        ):
            raise ValidationError(
                {
                    "effective_to":
                    (
                        "Effective to date cannot be "
                        "earlier than effective from date."
                    )
                }
            )

        # Structure must belong to same company
        if (
            self.structure
            and self.company
            and self.structure.company != self.company
        ):
            raise ValidationError(
                {
                    "structure":
                    (
                        "Salary structure does not "
                        "belong to this company."
                    )
                }
            )

        # Employee must belong to same company
        if (
            self.employee
            and self.company
            and self.employee.company != self.company
        ):
            raise ValidationError(
                {
                    "employee":
                    (
                        "Employee does not belong "
                        "to this company."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.remarks:
            self.remarks = self.remarks.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" - "
            f"₹{self.basic_salary}"
            f" (from {self.effective_from})"
        )
    

# ==========================================================
# PAYROLL CYCLE
# ==========================================================

class PayrollCycleStatus(models.TextChoices):
    DRAFT     = "Draft",     "Draft"
    ACTIVE    = "Active",    "Active"
    CLOSED    = "Closed",    "Closed"
    CANCELLED = "Cancelled", "Cancelled"


class PayrollCycle(models.Model):
    """
    Defines a payroll processing period.

    A PayrollCycle represents one month's
    payroll period for a company.

    Examples:
        June 2026 Payroll
        July 2026 Payroll

    Why a separate model?
        Because a payroll period has its own
        lifecycle — it opens, runs, gets approved,
        and closes. Multiple payroll runs can happen
        within one cycle (e.g. corrections).

    Lifecycle:
        Draft     → Being configured
        Active    → PayrollRun can be created
        Closed    → All payslips finalized
        Cancelled → Cycle abandoned

    Immutability:
        Once Closed, a cycle cannot be reopened.
        A new cycle must be created for corrections.

    Integration:
        Attendance data is read for this cycle's
        date range.
        Leave data is read for this cycle's
        date range.
        PayrollRun belongs to this cycle.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payroll_cycles",
    )

    # ──────────────────────────────────────
    # PERIOD
    # ──────────────────────────────────────

    month = models.PositiveSmallIntegerField(
        help_text="Month number (1-12).",
    )

    year = models.PositiveSmallIntegerField(
        help_text="Four-digit year.",
    )

    start_date = models.DateField(
        help_text="First day of the payroll period.",
    )

    end_date = models.DateField(
        help_text="Last day of the payroll period.",
    )

    # ──────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=PayrollCycleStatus.choices,
        default=PayrollCycleStatus.DRAFT,
    )

    # ──────────────────────────────────────
    # WORKING DAYS
    # ──────────────────────────────────────

    total_working_days = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Total working days in this cycle. "
            "Used to calculate per-day salary."
        ),
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    remarks = models.TextField(
        blank=True,
        default="",
    )

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_payroll_cycles",
    )

    closed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closed_payroll_cycles",
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "company",
            "-year",
            "-month",
        ]

        verbose_name = "Payroll Cycle"

        verbose_name_plural = "Payroll Cycles"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "company",
                    "month",
                    "year",
                ],
                name="unique_payroll_cycle_per_month_year",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["status"],
            ),

            models.Index(
                fields=["year", "month"],
            ),

            models.Index(
                fields=["start_date"],
            ),

            models.Index(
                fields=["end_date"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.remarks is not None:
            self.remarks = self.remarks.strip()

        # Month must be between 1 and 12
        if (
            self.month is not None
            and not 1 <= self.month <= 12
        ):
            raise ValidationError(
                {
                    "month":
                    "Month must be between 1 and 12."
                }
            )

        # Year must be reasonable
        if (
            self.year is not None
            and not 2000 <= self.year <= 2100
        ):
            raise ValidationError(
                {
                    "year":
                    "Year must be between 2000 and 2100."
                }
            )

        # end_date must be after start_date
        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                {
                    "end_date":
                    (
                        "End date cannot be earlier "
                        "than start date."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.remarks:
            self.remarks = self.remarks.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def period_label(self):
        """
        Returns a human-readable label for this cycle.
        Example: June 2026
        """
        from calendar import month_name

        if 1 <= self.month <= 12:
            return f"{month_name[self.month]} {self.year}"

        return f"Invalid Month ({self.month}) {self.year}"

    @property
    def is_closed(self):
        """
        Returns True if this cycle is closed
        and cannot be modified.
        """
        return self.status == PayrollCycleStatus.CLOSED

    @property
    def is_editable(self):
        """
        Returns True if payroll runs can be
        created or modified within this cycle.
        """
        return self.status in (
            PayrollCycleStatus.DRAFT,
            PayrollCycleStatus.ACTIVE,
        )

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.company.company_name}"
            f" - "
            f"{self.period_label}"
        )

# ==========================================================
# PAYROLL RUN STATUS
# ==========================================================

class PayrollRunStatus(models.TextChoices):
    DRAFT     = "Draft",     "Draft"
    PROCESSING = "Processing", "Processing"
    PROCESSED  = "Processed",  "Processed"
    APPROVED   = "Approved",   "Approved"
    FINALIZED  = "Finalized",  "Finalized"
    CANCELLED  = "Cancelled",  "Cancelled"


# ==========================================================
# PAYROLL RUN
# ==========================================================

class PayrollRun(models.Model):
    """
    Represents one execution of payroll within a cycle.

    A PayrollCycle can have multiple PayrollRuns.
    For example:
        Run 1 → Initial payroll
        Run 2 → Correction run for missed employees

    Why separate from PayrollCycle?
        Because processing payroll is a distinct
        action from defining the period.
        A cycle is the period. A run is the execution.

    Lifecycle:
        Draft      → Run created, not yet processed
        Processing → Payroll engine is running
        Processed  → All payslips generated
        Approved   → HR/Finance approved the run
        Finalized  → Payslips locked, cannot change
        Cancelled  → Run abandoned

    Immutability:
        Once Finalized, a PayrollRun cannot be
        modified. A new run must be created for
        corrections.

    Idempotency:
        Running payroll twice for the same run
        should not create duplicate payslips.
        The payroll service must handle this.

    Audit:
        Every status change records who did it
        and when.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payroll_runs",
    )

    cycle = models.ForeignKey(
        PayrollCycle,
        on_delete=models.PROTECT,
        related_name="payroll_runs",
        help_text=(
            "The payroll cycle this run belongs to."
        ),
    )

    # ──────────────────────────────────────
    # RUN IDENTITY
    # ──────────────────────────────────────

    run_number = models.PositiveSmallIntegerField(
        default=1,
        help_text=(
            "Run number within the cycle. "
            "First run is 1, correction is 2, etc."
        ),
    )

    description = models.TextField(
        blank=True,
        default="",
        help_text=(
            "e.g. Initial Run, Correction Run, "
            "Bonus Run."
        ),
    )

    # ──────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=PayrollRunStatus.choices,
        default=PayrollRunStatus.DRAFT,
    )

    # ──────────────────────────────────────
    # SUMMARY TOTALS
    # Populated after payroll processing.
    # ──────────────────────────────────────

    total_employees = models.PositiveIntegerField(
        default=0,
        help_text="Number of employees in this run.",
    )

    total_gross = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Sum of all gross salaries.",
    )

    total_deductions = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Sum of all deductions.",
    )

    total_net = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text="Sum of all net salaries.",
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_payroll_runs",
    )

    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_payroll_runs",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    finalized_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finalized_payroll_runs",
    )

    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "company",
            "-created_at",
        ]

        verbose_name = "Payroll Run"

        verbose_name_plural = "Payroll Runs"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "cycle",
                    "run_number",
                ],
                name="unique_run_number_per_cycle",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["cycle"],
            ),

            models.Index(
                fields=["status"],
            ),

            models.Index(
                fields=["created_at"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.description is not None:
            self.description = self.description.strip()

        if self.remarks is not None:
            self.remarks = self.remarks.strip()

        # Cycle must belong to same company
        if (
            self.cycle
            and self.company
            and self.cycle.company != self.company
        ):
            raise ValidationError(
                {
                    "cycle":
                    (
                        "Payroll cycle does not "
                        "belong to this company."
                    )
                }
            )

        # Cannot create a run on a closed cycle
        if (
            self.cycle
            and self.cycle.status == PayrollCycleStatus.CLOSED
            and not self.pk
        ):
            raise ValidationError(
                {
                    "cycle":
                    (
                        "Cannot create a payroll run "
                        "on a closed cycle."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.description:
            self.description = self.description.strip()

        if self.remarks:
            self.remarks = self.remarks.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def is_finalized(self):
        """
        Returns True if this run is finalized
        and completely locked.
        """
        return self.status == PayrollRunStatus.FINALIZED

    @property
    def is_editable(self):
        """
        Returns True if this run can still
        be modified.
        """
        return self.status in (
            PayrollRunStatus.DRAFT,
            PayrollRunStatus.PROCESSED,
        )

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.cycle}"
            f" — Run {self.run_number}"
        )
    

# ==========================================================
# PAYROLL ITEM
# ==========================================================

class PayrollItem(models.Model):
    """
    Stores one salary component line item
    for one employee in one payroll run.

    Every payslip is built from multiple
    PayrollItems — one per salary component.

    Examples for one employee in June 2026:
        Basic Salary    Earning    ₹50,000
        HRA             Earning    ₹25,000
        Special Allow   Earning    ₹5,000
        PF              Deduction  ₹6,000
        Professional Tax Deduction ₹200
        TDS             Deduction  ₹3,000

    Why store items separately from Payslip?
        Because payroll auditing requires knowing
        exactly which component contributed how much.
        A single net salary figure is not enough
        for compliance or AI analytics.

    Immutability:
        Once the PayrollRun is Finalized,
        PayrollItems are completely locked.
        No edits allowed after finalization.

    Snapshots:
        component_name and component_type are
        snapshotted at generation time.
        If a component is renamed or deleted later,
        historical payslips remain accurate.

    AI readiness:
        Each item exposes component_type,
        is_taxable, calculation_type, and
        base_amount, making it straightforward
        for AI to analyze salary trends,
        detect anomalies, and forecast costs.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payroll_items",
    )

    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="payroll_items",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="payroll_items",
    )

    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        related_name="payroll_items",
        help_text=(
            "The salary component this "
            "item represents."
        ),
    )

    # ──────────────────────────────────────
    # SNAPSHOT FIELDS
    # Captured at generation time.
    # Never change after creation.
    # ──────────────────────────────────────

    component_name = models.CharField(
        max_length=150,
        help_text=(
            "Snapshot of component name "
            "at generation time."
        ),
    )

    component_type = models.CharField(
        max_length=20,
        choices=ComponentType.choices,
        help_text=(
            "Snapshot of component type "
            "at generation time."
        ),
    )

    calculation_type = models.CharField(
        max_length=20,
        choices=CalculationType.choices,
        help_text=(
            "Snapshot of calculation type "
            "at generation time."
        ),
    )

    is_taxable = models.BooleanField(
        default=False,
        help_text=(
            "Snapshot of taxable status "
            "at generation time."
        ),
    )

    # ──────────────────────────────────────
    # CALCULATION INPUTS
    # ──────────────────────────────────────

    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=(
            "The basic salary used as base "
            "for percentage calculations."
        ),
    )

    rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text=(
            "The rate or fixed amount used "
            "for this component."
        ),
    )

    # ──────────────────────────────────────
    # CALCULATED RESULT
    # ──────────────────────────────────────

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=(
            "The final calculated amount "
            "for this component."
        ),
    )

    # ──────────────────────────────────────
    # DISPLAY
    # ──────────────────────────────────────

    display_order = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Controls the order in which this "
            "item appears on the payslip."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "employee",
            "display_order",
            "component_type",
        ]

        verbose_name = "Payroll Item"

        verbose_name_plural = "Payroll Items"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "payroll_run",
                    "employee",
                    "component",
                ],
                name="unique_component_per_employee_per_run",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["payroll_run"],
            ),

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["component"],
            ),

            models.Index(
                fields=["component_type"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.component_name is not None:
            self.component_name = (
                self.component_name.strip()
            )

        if not self.component_name:
            raise ValidationError(
                {
                    "component_name":
                    "Component name snapshot is required."
                }
            )

        if (
            self.amount is not None
            and self.amount < 0
        ):
            raise ValidationError(
                {
                    "amount":
                    "Payroll item amount cannot be negative."
                }
            )

        # Employee must belong to same company
        if (
            self.employee
            and self.company
            and self.employee.company != self.company
        ):
            raise ValidationError(
                {
                    "employee":
                    (
                        "Employee does not belong "
                        "to this company."
                    )
                }
            )

        # PayrollRun must belong to same company
        if (
            self.payroll_run
            and self.company
            and self.payroll_run.company != self.company
        ):
            raise ValidationError(
                {
                    "payroll_run":
                    (
                        "Payroll run does not belong "
                        "to this company."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        # Populate snapshots from component
        # on first save only
        if not self.pk and self.component:

            if not self.component_name:
                self.component_name = (
                    self.component.name
                )

            if not self.component_type:
                self.component_type = (
                    self.component.component_type
                )

            if not self.calculation_type:
                self.calculation_type = (
                    self.component.calculation_type
                )

            if not self.is_taxable:
                self.is_taxable = (
                    self.component.is_taxable
                )

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" — "
            f"{self.component_name}"
            f" ₹{self.amount}"
        )
    

# ==========================================================
# PAYSLIP STATUS
# ==========================================================

class PayslipStatus(models.TextChoices):
    DRAFT = "Draft", "Draft"
    GENERATED = "Generated", "Generated"
    ISSUED = "Issued", "Issued"
    CANCELLED = "Cancelled", "Cancelled"

# ==========================================================
# PAYSLIP
# ==========================================================

class Payslip(models.Model):
    """
    Represents the final payroll document issued
    to an employee for a payroll run.

    A Payslip summarizes payroll calculations for
    one employee. Detailed earnings and deductions
    are stored separately in PayrollItem.

    Responsibilities
    ----------------
    - Store final salary summary
    - Preserve historical payroll data
    - Record issue information
    - Provide employee-facing payroll document

    Immutability
    ------------
    Once issued, a payslip should never be edited.
    Any correction must generate a new PayrollRun
    and a new Payslip.

    Integration
    -----------
    - Belongs to one PayrollRun
    - Belongs to one Employee
    - References one EmployeeSalary
    - Uses PayrollItems for detailed breakdown
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payslips",
    )

    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.PROTECT,
        related_name="payslips",
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="payslips",
    )

    employee_salary = models.ForeignKey(
        EmployeeSalary,
        on_delete=models.PROTECT,
        related_name="payslips",
        help_text=(
            "Salary record used to generate "
            "this payslip."
        ),
    )   


        # ──────────────────────────────────────
    # SALARY SUMMARY (SNAPSHOTS)
    # ──────────────────────────────────────

    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=(
            "Snapshot of the employee's "
            "basic salary."
        ),
    )

    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=(
            "Total earnings before deductions."
        ),
    )

    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=(
            "Total deductions applied."
        ),
    )

    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=(
            "Final payable salary."
        ),
    )

    # ──────────────────────────────────────
    # PAYROLL PERIOD (SNAPSHOT)
    # ──────────────────────────────────────

    period_start = models.DateField(
        help_text=(
            "Payroll period start date."
        ),
    )

    period_end = models.DateField(
        help_text=(
            "Payroll period end date."
        ),
    )

        # ──────────────────────────────────────
    # ATTENDANCE SUMMARY (SNAPSHOT)
    # ──────────────────────────────────────

    working_days = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Total payable working days."
        ),
    )

    present_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text=(
            "Employee present days."
        ),
    )

    paid_leave_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text=(
            "Approved paid leave days."
        ),
    )

    loss_of_pay_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        help_text=(
            "Leave without pay days."
        ),
    )

    # ──────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=PayslipStatus.choices,
        default=PayslipStatus.DRAFT,
    )


    # ──────────────────────────────────────
    # ISSUE INFORMATION
    # ──────────────────────────────────────

    issued_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_payslips",
    )

    issued_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    remarks = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "employee",
            "-created_at",
        ]

        verbose_name = "Payslip"

        verbose_name_plural = "Payslips"

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "payroll_run",
                    "employee",
                ],
                name="unique_payslip_per_employee_per_run",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["payroll_run"],
            ),

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["status"],
            ),

        ]

    def clean(self):

        super().clean()

        if self.remarks is not None:
            self.remarks = self.remarks.strip()

        if (
            self.period_end
            and self.period_start
            and self.period_end < self.period_start
        ):
            raise ValidationError(
                {
                    "period_end":
                    (
                        "Period end cannot be "
                        "earlier than period start."
                    )
                }
            )

        if (
            self.company
            and self.employee
            and self.employee.company != self.company
        ):
            raise ValidationError(
                {
                    "employee":
                    (
                        "Employee does not belong "
                        "to this company."
                    )
                }
            )

        if (
            self.company
            and self.payroll_run
            and self.payroll_run.company != self.company
        ):
            raise ValidationError(
                {
                    "payroll_run":
                    (
                        "Payroll run does not belong "
                        "to this company."
                    )
                }
            )

        if (
            self.employee_salary
            and self.employee
            and self.employee_salary.employee != self.employee
        ):
            raise ValidationError(
                {
                    "employee_salary":
                    (
                        "Salary record does not belong "
                        "to this employee."
                    )
                }
            )

        if (
            self.company
            and self.employee_salary
            and self.employee_salary.company != self.company
        ):
            raise ValidationError(
                {
                    "employee_salary":
                    (
                        "Salary record does not belong "
                        "to this company."
                    )
                }
            )
        
    def save(self, *args, **kwargs):

        if self.remarks:
            self.remarks = self.remarks.strip()

        self.full_clean()

        super().save(*args, **kwargs)


    def __str__(self):

        return (
            f"{self.employee.employee_id}"
            f" - "
            f"{self.payroll_run}"
        )
    

