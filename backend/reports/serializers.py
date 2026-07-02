from rest_framework import serializers


# ==========================================================
# EMPLOYEE REPORT SERIALIZERS
# ==========================================================

class EmployeeSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for employee_summary().
    Returns high-level KPIs.
    """

    total                = serializers.IntegerField()
    active               = serializers.IntegerField()
    inactive             = serializers.IntegerField()
    on_probation         = serializers.IntegerField()
    new_this_month       = serializers.IntegerField()
    resigned_this_month  = serializers.IntegerField()


class EmployeeRegisterSerializer(
    serializers.Serializer,
):
    """
    Serializer for employee_register(),
    employees_by_department(), employees_by_designation(),
    employees_by_status(), joining_report(),
    resignation_report().

    All of these return Employee querysets or
    annotated value dicts — fields cover both cases.
    """

    # Core identification
    id              = serializers.IntegerField(read_only=True)
    employee_id     = serializers.CharField(read_only=True)
    full_name       = serializers.CharField(read_only=True)

    # Personal
    gender          = serializers.CharField(read_only=True)
    date_of_birth   = serializers.DateField(read_only=True)
    marital_status  = serializers.CharField(read_only=True)

    # Contact
    email           = serializers.EmailField(read_only=True)
    phone           = serializers.CharField(read_only=True)

    # Organization
    department      = serializers.SerializerMethodField()
    designation     = serializers.SerializerMethodField()

    # Employment
    employment_type = serializers.CharField(read_only=True)
    employee_status = serializers.CharField(read_only=True)
    joining_date    = serializers.DateField(read_only=True)
    is_active       = serializers.BooleanField(read_only=True)

    # Optional — populated for resigned/terminated
    resignation_date  = serializers.DateField(
        read_only=True,
        allow_null=True,
    )
    termination_date  = serializers.DateField(
        read_only=True,
        allow_null=True,
    )

    # Annotated fields — populated when returned by
    # employees_by_department / employees_by_designation /
    # employees_by_status
    employee_count  = serializers.IntegerField(
        read_only=True,
        required=False,
    )
    count           = serializers.IntegerField(
        read_only=True,
        required=False,
    )

    def get_department(self, obj):
        if hasattr(obj, "department") and obj.department:
            return obj.department.department_name
        # annotated queryset key
        return obj.get(
            "department__department_name",
            None,
        ) if hasattr(obj, "get") else None

    def get_designation(self, obj):
        if hasattr(obj, "designation") and obj.designation:
            return obj.designation.designation_name
        return obj.get(
            "designation__designation_name",
            None,
        ) if hasattr(obj, "get") else None


class EmployeeTrendSerializer(
    serializers.Serializer,
):
    """
    Serializer for headcount_trend().
    Returns month + joining count per month.
    """

    month    = serializers.DateField()
    joinings = serializers.IntegerField()


# ==========================================================
# ATTENDANCE REPORT SERIALIZERS
# ==========================================================

class AttendanceSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for attendance_summary().
    Returns company-wide KPIs for a month/year.
    """

    total_records          = serializers.IntegerField()
    present_count          = serializers.IntegerField()
    absent_count           = serializers.IntegerField()
    half_day_count         = serializers.IntegerField()
    leave_count            = serializers.IntegerField()
    late_count             = serializers.IntegerField()
    total_working_minutes  = serializers.IntegerField()
    total_overtime_minutes = serializers.IntegerField()
    total_late_minutes     = serializers.IntegerField()


class DailyAttendanceSerializer(
    serializers.Serializer,
):
    """
    Serializer for daily_report().
    Each row is one attendance record for a date.
    """

    id              = serializers.IntegerField()
    employee_id     = serializers.CharField()
    employee_name   = serializers.CharField()
    department      = serializers.CharField(allow_null=True)
    designation     = serializers.CharField(allow_null=True)
    shift_name      = serializers.CharField(allow_null=True)
    date            = serializers.DateField()
    check_in        = serializers.DateTimeField(allow_null=True)
    check_out       = serializers.DateTimeField(allow_null=True)
    working_minutes = serializers.IntegerField()
    late_minutes    = serializers.IntegerField()
    early_exit_minutes = serializers.IntegerField()
    overtime_minutes   = serializers.IntegerField()
    status             = serializers.CharField()
    attendance_source  = serializers.CharField()
    approval_status    = serializers.CharField()


class EmployeeAttendanceHistorySerializer(
    serializers.Serializer,
):
    """
    Serializer for employee_history().
    One row per attendance record for one employee.
    """

    id                 = serializers.IntegerField()
    employee_id        = serializers.CharField()
    employee_name      = serializers.CharField()
    department         = serializers.CharField(allow_null=True)
    designation        = serializers.CharField(allow_null=True)
    date               = serializers.DateField()
    check_in           = serializers.DateTimeField(allow_null=True)
    check_out          = serializers.DateTimeField(allow_null=True)
    working_minutes    = serializers.IntegerField()
    late_minutes       = serializers.IntegerField()
    early_exit_minutes = serializers.IntegerField()
    overtime_minutes   = serializers.IntegerField()
    status             = serializers.CharField()
    remarks            = serializers.CharField(allow_blank=True)
    attendance_source  = serializers.CharField()
    attendance_modified = serializers.BooleanField()
    approval_status    = serializers.CharField()


class MonthlyAttendanceSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for monthly_summary() and
    employee_attendance_summary().
    One row per employee with monthly totals.
    """

    employee_id            = serializers.CharField()
    employee_name          = serializers.SerializerMethodField()
    department             = serializers.SerializerMethodField()
    designation            = serializers.SerializerMethodField()
    present_count          = serializers.IntegerField()
    absent_count           = serializers.IntegerField()
    half_day_count         = serializers.IntegerField()
    leave_count            = serializers.IntegerField()
    late_count             = serializers.IntegerField()
    total_working_minutes  = serializers.IntegerField()
    total_overtime_minutes = serializers.IntegerField()
    total_late_minutes     = serializers.IntegerField()

    def get_employee_name(self, obj):
        # attendance/reports.py monthly_summary returns dicts
        if isinstance(obj, dict):
            return obj.get("employee_name", "")
        # reports/services.py employee_attendance_summary
        # returns ORM value dicts
        first  = obj.get("employee__first_name", "")
        middle = obj.get("employee__middle_name", "")
        last   = obj.get("employee__last_name", "")
        parts  = [p for p in [first, middle, last] if p]
        return " ".join(parts)

    def get_department(self, obj):
        if isinstance(obj, dict):
            return obj.get(
                "department",
                obj.get(
                    "employee__department__department_name",
                    None,
                ),
            )
        return None

    def get_designation(self, obj):
        if isinstance(obj, dict):
            return obj.get(
                "designation",
                obj.get(
                    "employee__designation__designation_name",
                    None,
                ),
            )
        return None


class DepartmentAttendanceSerializer(
    serializers.Serializer,
):
    """
    Serializer for department_attendance_summary().
    One row per department with monthly totals.
    """

    department_id          = serializers.IntegerField(
        source="employee__department__id",
    )
    department_name        = serializers.CharField(
        source="employee__department__department_name",
    )
    present_count          = serializers.IntegerField()
    absent_count           = serializers.IntegerField()
    half_day_count         = serializers.IntegerField()
    leave_count            = serializers.IntegerField()
    late_count             = serializers.IntegerField()
    total_working_minutes  = serializers.IntegerField()


class AttendanceDashboardSerializer(
    serializers.Serializer,
):
    """
    Serializer for dashboard().
    Single dict of today's KPIs.
    """

    date                  = serializers.DateField()
    total_employees       = serializers.IntegerField()
    present_count         = serializers.IntegerField()
    absent_count          = serializers.IntegerField()
    late_count            = serializers.IntegerField()
    on_leave_count        = serializers.IntegerField()
    half_day_count        = serializers.IntegerField()
    not_marked            = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class AttendanceTrendSerializer(
    serializers.Serializer,
):
    """
    Serializer for attendance_trend().
    One row per month.
    """

    month          = serializers.DateField()
    present_count  = serializers.IntegerField()
    absent_count   = serializers.IntegerField()
    half_day_count = serializers.IntegerField()
    leave_count    = serializers.IntegerField()
    late_count     = serializers.IntegerField()


class AttendanceExceptionSerializer(
    serializers.Serializer,
):
    """
    Serializer for exceptions().
    One row per anomalous attendance record.
    """

    id                  = serializers.IntegerField()
    employee_id         = serializers.CharField()
    employee_name       = serializers.CharField()
    department          = serializers.CharField(allow_null=True)
    designation         = serializers.CharField(allow_null=True)
    date                = serializers.DateField()
    check_in            = serializers.DateTimeField(allow_null=True)
    check_out           = serializers.DateTimeField(allow_null=True)
    working_minutes     = serializers.IntegerField()
    late_minutes        = serializers.IntegerField()
    early_exit_minutes  = serializers.IntegerField()
    overtime_minutes    = serializers.IntegerField()
    status              = serializers.CharField()
    attendance_source   = serializers.CharField()
    attendance_modified = serializers.BooleanField()
    approval_status     = serializers.CharField()
    approval_reason     = serializers.CharField(allow_blank=True)
    remarks             = serializers.CharField(allow_blank=True)


class TopAbsenteesSerializer(
    serializers.Serializer,
):
    """
    Serializer for top_absentees().
    One row per employee, ordered by absent_days desc.
    """

    employee_id   = serializers.CharField(
        source="employee__employee_id",
    )
    first_name    = serializers.CharField(
        source="employee__first_name",
    )
    last_name     = serializers.CharField(
        source="employee__last_name",
    )
    department    = serializers.CharField(
        source="employee__department__department_name",
        allow_null=True,
    )
    absent_days   = serializers.IntegerField()


class BestAttendanceSerializer(
    serializers.Serializer,
):
    """
    Serializer for best_attendance().
    One row per employee, ordered by present_days desc.
    """

    employee_id   = serializers.CharField(
        source="employee__employee_id",
    )
    first_name    = serializers.CharField(
        source="employee__first_name",
    )
    last_name     = serializers.CharField(
        source="employee__last_name",
    )
    department    = serializers.CharField(
        source="employee__department__department_name",
        allow_null=True,
    )
    present_days  = serializers.IntegerField()


# ==========================================================
# LEAVE REPORT SERIALIZERS
# ==========================================================

class LeaveSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for leave_summary().
    Returns aggregate leave KPIs for a year.
    """

    total_requests   = serializers.IntegerField()
    approved         = serializers.IntegerField()
    pending          = serializers.IntegerField()
    rejected         = serializers.IntegerField()
    total_days_taken = serializers.FloatField()


class LeaveBalanceReportSerializer(
    serializers.Serializer,
):
    """
    Serializer for leave_balance_report().
    One row per employee / leave type balance.
    """

    employee_id    = serializers.CharField(
        source="employee.employee_id",
    )
    employee_name  = serializers.SerializerMethodField()
    department     = serializers.CharField(
        source="employee.department.department_name",
        allow_null=True,
    )
    leave_type     = serializers.CharField(
        source="leave_type.leave_name",
    )
    year           = serializers.IntegerField()
    allocated_days = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
    )
    used_days      = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
    )
    remaining_days = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
    )

    def get_employee_name(self, obj):
        return obj.employee.full_name


class LeaveHistorySerializer(
    serializers.Serializer,
):
    """
    Serializer for leave_history().
    One row per leave request.
    """

    id              = serializers.IntegerField()
    employee_id     = serializers.CharField(
        source="employee.employee_id",
    )
    employee_name   = serializers.SerializerMethodField()
    department      = serializers.CharField(
        source="employee.department.department_name",
        allow_null=True,
    )
    leave_type      = serializers.CharField(
        source="leave_type_snapshot",
    )
    start_date      = serializers.DateField()
    end_date        = serializers.DateField()
    total_days      = serializers.DecimalField(
        max_digits=4,
        decimal_places=1,
    )
    is_half_day     = serializers.BooleanField()
    leave_status    = serializers.CharField()
    approval_status = serializers.CharField()
    reason          = serializers.CharField()
    request_date    = serializers.DateField()

    def get_employee_name(self, obj):
        return obj.employee.full_name


class DepartmentLeaveSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for department_leave_summary().
    One row per department.
    """

    department_name  = serializers.CharField(
        source="employee__department__department_name",
    )
    total_leave_days = serializers.FloatField()
    total_requests   = serializers.IntegerField()


class LeaveTrendSerializer(
    serializers.Serializer,
):
    """
    Serializer for leave_trend().
    One row per month.
    """

    month         = serializers.DateField()
    request_count = serializers.IntegerField()
    total_days    = serializers.FloatField()


# ==========================================================
# PAYROLL REPORT SERIALIZERS
# ==========================================================

class PayrollSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for payroll_summary().
    Returns aggregate payroll KPIs for a year.
    """

    total_payslips   = serializers.IntegerField()
    total_gross      = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    total_net        = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    total_deductions = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    avg_net_salary   = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )


class PayrollRegisterSerializer(
    serializers.Serializer,
):
    """
    Serializer for payroll_register().
    One row per payslip.
    """

    id               = serializers.IntegerField()
    employee_id      = serializers.CharField(
        source="employee.employee_id",
    )
    employee_name    = serializers.SerializerMethodField()
    department       = serializers.CharField(
        source="employee.department.department_name",
        allow_null=True,
    )
    designation      = serializers.CharField(
        source="employee.designation.designation_name",
        allow_null=True,
    )
    period_start     = serializers.DateField()
    period_end       = serializers.DateField()
    basic_salary     = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    gross_salary     = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total_deductions = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    net_salary       = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    status           = serializers.CharField()

    def get_employee_name(self, obj):
        return obj.employee.full_name


class DepartmentSalaryCostSerializer(
    serializers.Serializer,
):
    """
    Serializer for department_salary_cost().
    One row per department.
    """

    department_name  = serializers.CharField(
        source="employee__department__department_name",
        allow_null=True,
    )
    total_gross      = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    total_net        = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    total_deductions = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    employee_count   = serializers.IntegerField()


class PayrollTrendSerializer(
    serializers.Serializer,
):
    """
    Serializer for payroll_trend().
    One row per month.
    """

    month          = serializers.IntegerField()
    total_gross    = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    total_net      = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    employee_count = serializers.IntegerField()


class HighestEarnersSerializer(
    serializers.Serializer,
):
    """
    Serializer for highest_earners().
    One row per employee ordered by avg net salary desc.
    """

    employee_id  = serializers.CharField(
        source="employee__employee_id",
    )
    first_name   = serializers.CharField(
        source="employee__first_name",
    )
    last_name    = serializers.CharField(
        source="employee__last_name",
    )
    department   = serializers.CharField(
        source="employee__department__department_name",
        allow_null=True,
    )
    avg_net      = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


# ==========================================================
# INVENTORY REPORT SERIALIZERS
# ==========================================================

class InventorySummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for inventory_summary().
    Returns aggregate asset KPIs.
    """

    total_assets         = serializers.IntegerField()
    available            = serializers.IntegerField()
    assigned             = serializers.IntegerField()
    under_maintenance    = serializers.IntegerField()
    retired              = serializers.IntegerField()
    total_purchase_cost  = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )


class AssetRegisterSerializer(
    serializers.Serializer,
):
    """
    Serializer for asset_register() and retired_assets().
    One row per asset.
    """

    id             = serializers.IntegerField()
    asset_tag      = serializers.CharField()
    name           = serializers.CharField()
    category       = serializers.CharField(
        source="category.name",
        allow_null=True,
    )
    vendor         = serializers.CharField(
        source="vendor.name",
        allow_null=True,
    )
    status         = serializers.CharField()
    condition      = serializers.CharField()
    purchase_date  = serializers.DateField(allow_null=True)
    purchase_cost  = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
    )
    location       = serializers.CharField(allow_blank=True)
    is_active      = serializers.BooleanField()


class AssignedAssetSerializer(
    serializers.Serializer,
):
    """
    Serializer for assigned_assets().
    One row per active assignment.
    """

    id                    = serializers.IntegerField()
    asset_tag             = serializers.CharField(
        source="asset.asset_tag",
    )
    asset_name            = serializers.CharField(
        source="asset.name",
    )
    category              = serializers.CharField(
        source="asset.category.name",
        allow_null=True,
    )
    employee_id           = serializers.CharField(
        source="employee.employee_id",
    )
    employee_name         = serializers.SerializerMethodField()
    department            = serializers.CharField(
        source="employee.department.department_name",
        allow_null=True,
    )
    assigned_date         = serializers.DateField()
    assigned_condition    = serializers.CharField()
    asset_tag_snapshot    = serializers.CharField()
    employee_name_snapshot = serializers.CharField()

    def get_employee_name(self, obj):
        return obj.employee.full_name


class MaintenanceHistorySerializer(
    serializers.Serializer,
):
    """
    Serializer for maintenance_history().
    One row per maintenance record.
    """

    id               = serializers.IntegerField()
    asset_tag        = serializers.CharField(
        source="asset.asset_tag",
    )
    asset_name       = serializers.CharField(
        source="asset.name",
    )
    maintenance_type = serializers.CharField()
    status           = serializers.CharField()
    scheduled_date   = serializers.DateField()
    completed_date   = serializers.DateField(allow_null=True)
    cost             = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        allow_null=True,
    )
    description      = serializers.CharField(allow_blank=True)
    outcome_notes    = serializers.CharField(allow_blank=True)
    vendor           = serializers.CharField(
        source="vendor.name",
        allow_null=True,
    )


class MaintenanceTrendSerializer(
    serializers.Serializer,
):
    """
    Serializer for maintenance_cost_trend().
    One row per month.
    """

    month        = serializers.DateField()
    total_cost   = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    repair_count = serializers.IntegerField()


class MostMaintainedAssetSerializer(
    serializers.Serializer,
):
    """
    Serializer for most_maintained_assets().
    One row per asset ordered by maintenance_count desc.
    """

    asset_tag          = serializers.CharField(
        source="asset__asset_tag",
    )
    asset_name         = serializers.CharField(
        source="asset__name",
    )
    category           = serializers.CharField(
        source="asset__category__name",
        allow_null=True,
    )
    maintenance_count  = serializers.IntegerField()


class VendorAssetSerializer(
    serializers.Serializer,
):
    """
    Serializer for assets_by_vendor().
    One row per vendor.
    """

    vendor_id    = serializers.IntegerField(
        source="vendor__id",
        allow_null=True,
    )
    vendor_name  = serializers.CharField(
        source="vendor__name",
        allow_null=True,
    )
    asset_count  = serializers.IntegerField()
    total_cost   = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )


# ==========================================================
# PAYMENT REPORT SERIALIZERS
# ==========================================================

class PaymentSummarySerializer(
    serializers.Serializer,
):
    """
    Serializer for payment_summary().
    Returns aggregate payment KPIs for a year.
    """

    total_payments  = serializers.IntegerField()
    total_paid      = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    pending_count   = serializers.IntegerField()
    failed_count    = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()


class PaymentRegisterSerializer(
    serializers.Serializer,
):
    """
    Serializer for payment_register() and
    pending_payments() and failed_payments().
    One row per payment.
    """

    id                   = serializers.IntegerField()
    payment_number       = serializers.CharField()
    employee_id          = serializers.CharField(
        source="employee.employee_id",
    )
    employee_name        = serializers.SerializerMethodField()
    department           = serializers.CharField(
        source="employee.department.department_name",
        allow_null=True,
    )
    amount               = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    payment_method       = serializers.CharField()
    status               = serializers.CharField()
    payment_date         = serializers.DateField(allow_null=True)
    transaction_id       = serializers.CharField(allow_blank=True)
    bank_reference_number = serializers.CharField(allow_blank=True)
    failure_reason       = serializers.CharField(allow_blank=True)
    created_at           = serializers.DateTimeField()

    def get_employee_name(self, obj):
        return obj.employee.full_name


class PaymentTrendSerializer(
    serializers.Serializer,
):
    """
    Serializer for payment_trend().
    One row per month — paid payments only.
    """

    month         = serializers.DateField()
    total_paid    = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )
    payment_count = serializers.IntegerField()
