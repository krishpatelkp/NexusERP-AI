"""
==========================================================
NexusERP-AI Attendance Report Service
==========================================================

Single Responsibility:
    Fetching and aggregating attendance data for reports.

This service does NOT:
    - Handle check-in/check-out (that is services.py)
    - Modify any attendance records
    - Handle permissions (that is the view layer)

All methods accept a pre-filtered base queryset
from the view so company isolation is always
enforced before this service runs.
==========================================================
"""

from datetime import date
from calendar import monthrange

from django.db.models import (
    Avg,
    Case,
    Count,
    F,
    FloatField,
    IntegerField,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .models import (
    Attendance,
    AttendanceStatus,
)

from .constants import (
    FULL_DAY_MINUTES,
    HALF_DAY_MINUTES,
)


# ==========================================================
# ATTENDANCE REPORT SERVICE
# ==========================================================

class AttendanceReportService:
    """
    Generates all attendance reports for NexusERP.

    Methods
    -------
    daily_report()
        All employees attendance for a specific date.

    employee_history()
        One employee's attendance over a date range.

    monthly_summary()
        Per-employee totals for a given month and year.

    dashboard()
        Today's high-level attendance KPIs.

    exceptions()
        Records with anomalies flagged for HR review.
    """

    # def department_summary(
    #     self,
    #     month,
    #     year,
    # ):
    #     """
    #     Department-wise attendance summary.
    #     """

    #     queryset = (
    #         self._base_queryset()
    #         .filter(
    #             date__year=year,
    #             date__month=month,
    #         )
    #     )

    #     return (
    #         queryset
    #         .values(
    #             "employee__department__department_name",
    #         )
    #         .annotate(
    #             present=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.PRESENT),
    #             ),
    #             absent=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.ABSENT),
    #             ),
    #             half_day=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.HALF_DAY),
    #             ),
    #             leave=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.LEAVE),
    #             ),
    #             late=Count(
    #                 "id",
    #                 filter=Q(late_minutes__gt=0),
    #             ),
    #         )
    #         .order_by(
    #             "employee__department__department_name",
    #         )
    #     )
    


    # def attendance_trend(
    #     self,
    #     date_from,
    #     date_to,
    # ):
    #     """
    #     Daily attendance trend.
    #     """

    #     return (
    #         self._base_queryset()
    #         .filter(
    #             date__gte=date_from,
    #             date__lte=date_to,
    #         )
    #         .values("date")
    #         .annotate(
    #             present=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.PRESENT),
    #             ),
    #             absent=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.ABSENT),
    #             ),
    #             half_day=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.HALF_DAY),
    #             ),
    #             leave=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.LEAVE),
    #             ),
    #         )
    #         .order_by("date")
    #     )
    

    # def top_absentees(
    #     self,
    #     limit=10,
    # ):
    #     """
    #     Employees with the highest absences.
    #     """

    #     return (
    #         self._base_queryset()
    #         .values(
    #             "employee__employee_id",
    #             "employee__first_name",
    #             "employee__middle_name",
    #             "employee__last_name",
    #         )
    #         .annotate(
    #             absent_days=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.ABSENT),
    #             ),
    #         )
    #         .order_by("-absent_days")[:limit]
    #     )
    


    # def best_attendance(
    #     self,
    #     limit=10,
    # ):
    #     """
    #     Employees with the highest attendance.
    #     """

    #     return (
    #         self._base_queryset()
    #         .values(
    #             "employee__employee_id",
    #             "employee__first_name",
    #             "employee__middle_name",
    #             "employee__last_name",
    #         )
    #         .annotate(
    #             present_days=Count(
    #                 "id",
    #                 filter=Q(status=AttendanceStatus.PRESENT),
    #             ),
    #         )
    #         .order_by("-present_days")[:limit]
    #     )

    def __init__(self, company):
        """
        Every report is scoped to one company.
        This enforces company isolation at the
        service level, not just in views.
        """
        self.company = company

    # ======================================================
    # BASE QUERYSET
    # ======================================================

    def _base_queryset(self):
        """
        Returns the base queryset scoped to this company.

        All report methods call this first so
        company isolation is never accidentally skipped.
        """
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

    # ======================================================
    # DAILY REPORT
    # ======================================================

    def daily_report(self, report_date=None):
        """
        Returns all attendance records for a specific date.

        Parameters
        ----------
        report_date : date, optional
            The date to report on.
            Defaults to today if not provided.

        Returns
        -------
        QuerySet
            Attendance records for that date,
            ordered by employee ID.
        """

        if report_date is None:
            report_date = timezone.localdate()

        return (
            self._base_queryset()
            .filter(date=report_date)
            .order_by("employee__employee_id")
        )

    # ======================================================
    # EMPLOYEE HISTORY
    # ======================================================

    def employee_history(
        self,
        employee_id,
        date_from=None,
        date_to=None,
    ):
        """
        Returns attendance history for one employee
        over a date range.

        Parameters
        ----------
        employee_id : int
            The database PK of the employee.

        date_from : date, optional
            Start of date range.
            Defaults to 6 months ago.

        date_to : date, optional
            End of date range.
            Defaults to today.

        Returns
        -------
        QuerySet
            Attendance records for that employee,
            ordered by date descending.
        """

        from .constants import DEFAULT_HISTORY_MONTHS

        today = timezone.localdate()

        if date_to is None:
            date_to = today

        if date_from is None:
            date_from = today - relativedelta(
            months=DEFAULT_HISTORY_MONTHS,
)

        return (
            self._base_queryset()
            .filter(
                employee__id=employee_id,
                date__gte=date_from,
                date__lte=date_to,
            )
            .order_by("-date")
        )

    # ======================================================
    # MONTHLY SUMMARY
    # ======================================================

    def monthly_summary(self, month, year):
        """
        Returns aggregated attendance totals per employee
        for a given month and year.

        Parameters
        ----------
        month : int
            Month number (1-12).

        year : int
            Four-digit year.

        Returns
        -------
        list of dict
            One dict per employee with totals:
            present_days, absent_days, half_days,
            late_days, leave_days,
            total_working_minutes, total_overtime_minutes,
            total_late_minutes, average_working_minutes,
            attendance_percentage.
        """

        # Total working days in the month
        _, total_days_in_month = monthrange(year, month)

        queryset = (
            self._base_queryset()
            .filter(
                date__year=year,
                date__month=month,
            )
        )

        # Get all unique employees in this queryset
        employees = (
            queryset
            .values(
                "employee__id",
                "employee__employee_id",
                "employee__first_name",
                "employee__middle_name",
                "employee__last_name",
                "employee__department__department_name",
                "employee__designation__designation_name",
            )
            .distinct()
        )

        results = []

        for emp in employees:

            emp_id = emp["employee__id"]

            emp_records = queryset.filter(
                employee__id=emp_id,
            )

            # Aggregate counts
            present_days = emp_records.filter(
                status=AttendanceStatus.PRESENT,
            ).count()

            half_days = emp_records.filter(
                status=AttendanceStatus.HALF_DAY,
            ).count()

            absent_days = emp_records.filter(
                status=AttendanceStatus.ABSENT,
            ).count()

            late_days = emp_records.filter(
                late_minutes__gt=0,
            ).count()

            leave_days = emp_records.filter(
                status=AttendanceStatus.LEAVE,
            ).count()

            # Aggregate minutes
            totals = emp_records.aggregate(
                total_working=Sum("working_minutes"),
                total_overtime=Sum("overtime_minutes"),
                total_late=Sum("late_minutes"),
            )

            total_working = totals["total_working"] or 0
            total_overtime = totals["total_overtime"] or 0
            total_late = totals["total_late"] or 0

            # Calculate averages
            record_count = emp_records.count()

            average_working = (
                round(total_working / record_count, 2)
                if record_count > 0 else 0
            )

            # Attendance percentage
            # Present days + half days (counted as 0.5)
            effective_days = present_days + (half_days * 0.5)

            attendance_percentage = (
                round(
                    (effective_days / total_days_in_month) * 100,
                    2,
                )
                if total_days_in_month > 0 else 0
            )

            # Build full name
            middle = emp["employee__middle_name"]
            parts = [emp["employee__first_name"]]
            if middle:
                parts.append(middle)
            parts.append(emp["employee__last_name"])
            full_name = " ".join(parts)

            results.append(
                {
                    "employee_id":             emp["employee__employee_id"],
                    "employee_name":           full_name,
                    "department":              emp["employee__department__department_name"],
                    "designation":             emp["employee__designation__designation_name"],
                    "present_days":            present_days,
                    "absent_days":             absent_days,
                    "half_days":               half_days,
                    "late_days":               late_days,
                    "leave_days":              leave_days,
                    "total_working_minutes":   total_working,
                    "total_overtime_minutes":  total_overtime,
                    "total_late_minutes":      total_late,
                    "average_working_minutes": average_working,
                    "attendance_percentage":   attendance_percentage,
                }
            )

        return results

    # ======================================================
    # DASHBOARD
    # ======================================================

    def dashboard(self, dashboard_date=None):
        """
        Returns today's high-level attendance KPIs.

        Parameters
        ----------
        dashboard_date : date, optional
            Date for the dashboard.
            Defaults to today.

        Returns
        -------
        dict
            KPI counts for the dashboard.
        """

        if dashboard_date is None:
            dashboard_date = timezone.localdate()

        # Total active employees in company
        from employees.models import Employee

        total_employees = Employee.objects.filter(
            company=self.company,
            is_active=True,
        ).count()

        # Today's attendance records
        today_records = (
            self._base_queryset()
            .filter(date=dashboard_date)
        )

        present_count = today_records.filter(
            status=AttendanceStatus.PRESENT,
        ).count()

        absent_count = today_records.filter(
            status=AttendanceStatus.ABSENT,
        ).count()

        half_day_count = today_records.filter(
            status=AttendanceStatus.HALF_DAY,
        ).count()

        on_leave_count = today_records.filter(
            status=AttendanceStatus.LEAVE,
        ).count()

        late_count = today_records.filter(
            late_minutes__gt=0,
        ).count()

        # Employees with no attendance record today
        marked_employee_ids = today_records.values_list(
            "employee__id",
            flat=True,
        )

        not_marked = Employee.objects.filter(
            company=self.company,
            is_active=True,
        ).exclude(
            id__in=marked_employee_ids,
        ).count()

        # Attendance percentage
        attendance_percentage = (
            round(
                (present_count / total_employees) * 100,
                2,
            )
            if total_employees > 0 else 0
        )

        return {
            "date":                 dashboard_date,
            "total_employees":      total_employees,
            "present_count":        present_count,
            "absent_count":         absent_count,
            "late_count":           late_count,
            "on_leave_count":       on_leave_count,
            "half_day_count":       half_day_count,
            "not_marked":           not_marked,
            "attendance_percentage": attendance_percentage,
        }

    # ======================================================
    # EXCEPTIONS REPORT
    # ======================================================

    def exceptions(
        self,
        date_from=None,
        date_to=None,
    ):
        """
        Returns attendance records with anomalies
        flagged for HR review.

        Anomalies include:
        - Late arrivals (late_minutes > 0)
        - Early exits (early_exit_minutes > 0)
        - Missing check-in
        - Missing check-out
        - Manual entries
        - Modified records
        - Pending approval

        Parameters
        ----------
        date_from : date, optional
        date_to   : date, optional

        Returns
        -------
        QuerySet
            Anomalous attendance records.
        """

        from .models import AttendanceSource, ApprovalStatus

        today = timezone.localdate()

        if date_to is None:
            date_to = today

        if date_from is None:
            date_from = today

        return (
            self._base_queryset()
            .filter(
                date__gte=date_from,
                date__lte=date_to,
            )
            .filter(
                Q(late_minutes__gt=0)
                | Q(early_exit_minutes__gt=0)
                | Q(check_in__isnull=True)
                | Q(check_out__isnull=True)
                | Q(attendance_source=AttendanceSource.MANUAL)
                | Q(attendance_modified=True)
                | Q(approval_status=ApprovalStatus.PENDING)
            )
            .order_by("-date", "employee__employee_id")
        )