import django_filters
from django.db.models import Q

from .models import (
    Attendance,
    Holiday,
    AttendanceStatus,
    AttendanceSource,
    ApprovalStatus,
    HolidayType,
)


# ==========================================================
# ATTENDANCE FILTER
# ==========================================================

class AttendanceFilter(django_filters.FilterSet):
    """
    Filters for attendance report APIs.

    Company isolation is NOT handled here.
    The view's get_queryset() filters by company first.
    This filter works within that pre-filtered dataset.

    Supports:
    - Date range
    - Employee, Department, Designation, Shift
    - Status, Source, Approval
    - Late, Overtime, Early Exit, Missing Checkout
    - Working/Late/Overtime minute ranges
    - Full text search
    - Ordering
    """

    # ──────────────────────────────────────
    # DATE FILTERS
    # ──────────────────────────────────────

    date = django_filters.DateFilter(
        field_name="date",
    )

    date_from = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
    )

    date_to = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
    )

    # ──────────────────────────────────────
    # EMPLOYEE FILTERS
    # ──────────────────────────────────────

    employee = django_filters.NumberFilter(
        field_name="employee__id",
    )

    employee_id = django_filters.CharFilter(
        field_name="employee__employee_id",
        lookup_expr="iexact",
        label="Employee ID (e.g. EMP000001)",
    )

    department = django_filters.NumberFilter(
        field_name="employee__department__id",
    )

    designation = django_filters.NumberFilter(
        field_name="employee__designation__id",
    )

    shift = django_filters.NumberFilter(
        field_name="shift__id",
    )

    # ──────────────────────────────────────
    # STATUS FILTERS
    # ──────────────────────────────────────

    status = django_filters.ChoiceFilter(
        choices=AttendanceStatus.choices,
    )

    attendance_source = django_filters.ChoiceFilter(
        choices=AttendanceSource.choices,
    )

    approval_status = django_filters.ChoiceFilter(
        choices=ApprovalStatus.choices,
    )

    attendance_modified = django_filters.BooleanFilter(
        field_name="attendance_modified",
    )

    # ──────────────────────────────────────
    # EXCEPTION FILTERS
    # For the Exceptions Report
    # ──────────────────────────────────────

    is_late = django_filters.BooleanFilter(
        method="filter_late",
        label="Is Late",
    )

    has_overtime = django_filters.BooleanFilter(
        method="filter_overtime",
        label="Has Overtime",
    )

    has_early_exit = django_filters.BooleanFilter(
        method="filter_early_exit",
        label="Has Early Exit",
    )

    missing_checkin = django_filters.BooleanFilter(
        method="filter_missing_checkin",
        label="Missing Check-In",
    )

    missing_checkout = django_filters.BooleanFilter(
        method="filter_missing_checkout",
        label="Missing Check-Out",
    )

    manual_entry = django_filters.BooleanFilter(
        method="filter_manual_entry",
        label="Manual Entry",
    )

    pending_approval = django_filters.BooleanFilter(
        method="filter_pending_approval",
        label="Pending Approval",
    )

    # ──────────────────────────────────────
    # MINUTE RANGE FILTERS
    # ──────────────────────────────────────

    working_minutes_min = django_filters.NumberFilter(
        field_name="working_minutes",
        lookup_expr="gte",
    )

    working_minutes_max = django_filters.NumberFilter(
        field_name="working_minutes",
        lookup_expr="lte",
    )

    late_minutes_min = django_filters.NumberFilter(
        field_name="late_minutes",
        lookup_expr="gte",
    )

    late_minutes_max = django_filters.NumberFilter(
        field_name="late_minutes",
        lookup_expr="lte",
    )

    overtime_minutes_min = django_filters.NumberFilter(
        field_name="overtime_minutes",
        lookup_expr="gte",
    )

    overtime_minutes_max = django_filters.NumberFilter(
        field_name="overtime_minutes",
        lookup_expr="lte",
    )

    # ──────────────────────────────────────
    # ORDERING
    # ──────────────────────────────────────

    ordering = django_filters.OrderingFilter(
        fields=(
            ("date",             "date"),
            ("employee__id",     "employee"),
            ("working_minutes",  "working_minutes"),
            ("late_minutes",     "late_minutes"),
            ("overtime_minutes", "overtime_minutes"),
            ("status",           "status"),
        ),
        label="Ordering",
    )

    # ──────────────────────────────────────
    # SEARCH
    # ──────────────────────────────────────

    search = django_filters.CharFilter(
        method="filter_search",
        label="Search",
    )

    class Meta:
        model = Attendance
        fields = [
            "date",
            "date_from",
            "date_to",
            "employee",
            "employee_id",
            "department",
            "designation",
            "shift",
            "status",
            "attendance_source",
            "approval_status",
            "attendance_modified",
            "is_late",
            "has_overtime",
            "has_early_exit",
            "missing_checkin",
            "missing_checkout",
            "manual_entry",
            "pending_approval",
            "working_minutes_min",
            "working_minutes_max",
            "late_minutes_min",
            "late_minutes_max",
            "overtime_minutes_min",
            "overtime_minutes_max",
            "ordering",
            "search",
        ]

    # ──────────────────────────────────────
    # CUSTOM FILTER METHODS
    # ──────────────────────────────────────

    def filter_late(self, queryset, name, value):
        """
        Employees who arrived late.
        late_minutes > 0 means late.
        """
        if value:
            return queryset.filter(late_minutes__gt=0)
        return queryset.filter(late_minutes=0)

    def filter_overtime(self, queryset, name, value):
        """
        Employees who worked overtime.
        overtime_minutes > 0 means overtime.
        """
        if value:
            return queryset.filter(overtime_minutes__gt=0)
        return queryset.filter(overtime_minutes=0)

    def filter_early_exit(self, queryset, name, value):
        """
        Employees who left before shift end.
        early_exit_minutes > 0 means early exit.
        """
        if value:
            return queryset.filter(early_exit_minutes__gt=0)
        return queryset.filter(early_exit_minutes=0)

    def filter_missing_checkin(self, queryset, name, value):
        """
        Attendance records with no check-in at all.
        """
        if value:
            return queryset.filter(check_in__isnull=True)
        return queryset.filter(check_in__isnull=False)

    def filter_missing_checkout(self, queryset, name, value):
        """
        Employees who checked in but never checked out.
        """
        if value:
            return queryset.filter(
                check_in__isnull=False,
                check_out__isnull=True,
            )
        return queryset.filter(
            check_in__isnull=False,
            check_out__isnull=False,
        )

    def filter_manual_entry(self, queryset, name, value):
        """
        Records entered manually by HR.
        attendance_source = Manual
        """
        if value:
            return queryset.filter(
                attendance_source=AttendanceSource.MANUAL,
            )
        return queryset.exclude(
            attendance_source=AttendanceSource.MANUAL,
        )

    def filter_pending_approval(self, queryset, name, value):
        """
        Records waiting for HR approval.
        """
        if value:
            return queryset.filter(
                approval_status=ApprovalStatus.PENDING,
            )
        return queryset.exclude(
            approval_status=ApprovalStatus.PENDING,
        )

    def filter_search(self, queryset, name, value):
        """
        Search across employee name, email,
        employee ID, department name,
        designation name, and shift name.
        """
        return queryset.filter(
            Q(employee__first_name__icontains=value)
            | Q(employee__last_name__icontains=value)
            | Q(employee__email__icontains=value)
            | Q(employee__employee_id__icontains=value)
            | Q(employee__department__department_name__icontains=value)
            | Q(employee__designation__designation_name__icontains=value)
            | Q(shift_name_snapshot__icontains=value)
        )


# ==========================================================
# HOLIDAY FILTER
# ==========================================================

class HolidayFilter(django_filters.FilterSet):
    """
    Filters for the Holiday list API.

    Company isolation happens in the view.
    This filter works within that dataset.
    """

    date_from = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
    )

    date_to = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
    )

    holiday_type = django_filters.ChoiceFilter(
        choices=HolidayType.choices,
    )

    is_optional = django_filters.BooleanFilter(
        field_name="is_optional",
    )

    is_recurring = django_filters.BooleanFilter(
        field_name="is_recurring",
    )

    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )

    search = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Search by holiday name",
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("date", "date"),
            ("name", "name"),
        ),
        label="Ordering",
    )

    class Meta:
        model = Holiday
        fields = [
            "date_from",
            "date_to",
            "holiday_type",
            "is_optional",
            "is_recurring",
            "is_active",
            "search",
            "ordering",
        ]