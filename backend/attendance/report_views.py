"""
==========================================================
NexusERP-AI Attendance Report Views
==========================================================

Responsibilities
----------------
Each view is responsible for:
    1. Authenticating the user
    2. Validating query parameters
    3. Calling AttendanceReportService
    4. Serializing the response
    5. Returning the response

Each view is NOT responsible for:
    - ORM queries
    - Business logic
    - Attendance calculations
    - Aggregations

Architecture
------------
BaseAttendanceReportAPIView
        │
        ├── DailyAttendanceReportAPIView
        ├── EmployeeAttendanceHistoryAPIView
        ├── MonthlyAttendanceSummaryAPIView
        ├── AttendanceDashboardAPIView
        └── AttendanceExceptionAPIView
==========================================================
"""

from datetime import date

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .filters import AttendanceFilter
from .pagination import AttendanceReportPagination

from .report_serializers import (
    AttendanceDashboardSerializer,
    AttendanceExceptionSerializer,
    DailyAttendanceReportSerializer,
    EmployeeAttendanceHistorySerializer,
    MonthlyAttendanceSummarySerializer,
)

from .reports import AttendanceReportService


# ==========================================================
# BASE ATTENDANCE REPORT VIEW
# ==========================================================

class BaseAttendanceReportAPIView(
    generics.GenericAPIView,
):
    """
    Base class for all attendance report views.

    Provides:
    - JWT Authentication
    - Pagination
    - Filter backends
    - AttendanceFilter

    All report views inherit from this class.
    Shared configuration is defined here once.
    """

    permission_classes = (
        permissions.IsAuthenticated,
    )

    pagination_class = AttendanceReportPagination

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    )

    filterset_class = AttendanceFilter

    search_fields = (
        "employee__employee_id",
        "employee__first_name",
        "employee__last_name",
        "employee__email",
    )

    ordering_fields = (
        "date",
        "employee__employee_id",
        "working_minutes",
        "late_minutes",
        "overtime_minutes",
        "status",
    )

    ordering = ("-date",)

    def get_service(self):
        """
        Returns an AttendanceReportService instance
        scoped to the current user's company.

        Company isolation is enforced here so
        every report inherits it automatically.
        """
        return AttendanceReportService(
            company=self.request.user.company,
        )


# ==========================================================
# DAILY ATTENDANCE REPORT
# ==========================================================

class DailyAttendanceReportAPIView(
    BaseAttendanceReportAPIView,
):
    """
    GET /api/attendance/reports/daily/

    Returns all attendance records for a specific date.

    Query Parameters
    ----------------
    date : YYYY-MM-DD, optional
        The date to report on.
        Defaults to today.

    department : int, optional
        Filter by department ID.

    status : str, optional
        Filter by attendance status.

    is_late : bool, optional
        Filter late arrivals only.

    search : str, optional
        Search by employee name or ID.

    page : int, optional
        Page number. Default 1.

    page_size : int, optional
        Records per page. Max 100.

    Example
    -------
    GET /api/attendance/reports/daily/?date=2026-06-27
    GET /api/attendance/reports/daily/?date=2026-06-27&status=Present
    GET /api/attendance/reports/daily/?date=2026-06-27&is_late=true
    """

    serializer_class = DailyAttendanceReportSerializer

    def get(self, request, *args, **kwargs):

        # ── 1. Parse date parameter ──────────────────────
        date_param = request.query_params.get("date")

        if date_param:
            try:
                report_date = date.fromisoformat(date_param)
            except ValueError:
                return Response(
                    {
                        "error": (
                            "Invalid date format. "
                            "Use YYYY-MM-DD."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            report_date = None

        # ── 2. Call service ──────────────────────────────
        service = self.get_service()
        queryset = service.daily_report(
            report_date=report_date,
        )

        # ── 3. Apply filters ─────────────────────────────
        queryset = self.filter_queryset(queryset)

        # ── 4. Paginate ──────────────────────────────────
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(
                serializer.data,
            )

        # ── 5. Serialize and return ──────────────────────
        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# EMPLOYEE ATTENDANCE HISTORY
# ==========================================================

class EmployeeAttendanceHistoryAPIView(
    BaseAttendanceReportAPIView,
):
    """
    GET /api/attendance/reports/employee/

    Returns attendance history for one employee
    over a date range.

    Query Parameters
    ----------------
    employee_id : int, required
        Database PK of the employee.

    date_from : YYYY-MM-DD, optional
        Start of date range.
        Defaults to 6 months ago.

    date_to : YYYY-MM-DD, optional
        End of date range.
        Defaults to today.

    Example
    -------
    GET /api/attendance/reports/employee/?employee_id=1
    GET /api/attendance/reports/employee/?employee_id=1&date_from=2026-01-01&date_to=2026-06-30
    """

    serializer_class = EmployeeAttendanceHistorySerializer

    def get(self, request, *args, **kwargs):

        # ── 1. Validate employee_id ──────────────────────
        employee_id = request.query_params.get(
            "employee_id",
        )

        if not employee_id:
            return Response(
                {
                    "error": (
                        "employee_id is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            employee_id = int(employee_id)
        except ValueError:
            return Response(
                {
                    "error": (
                        "employee_id must be an integer."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── 2. Parse date range ──────────────────────────
        date_from_param = request.query_params.get(
            "date_from",
        )
        date_to_param = request.query_params.get(
            "date_to",
        )

        try:
            date_from = (
                date.fromisoformat(date_from_param)
                if date_from_param else None
            )
            date_to = (
                date.fromisoformat(date_to_param)
                if date_to_param else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        "Invalid date format. "
                        "Use YYYY-MM-DD."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── 3. Call service ──────────────────────────────
        service = self.get_service()
        queryset = service.employee_history(
            employee_id=employee_id,
            date_from=date_from,
            date_to=date_to,
        )

        # ── 4. Apply filters ─────────────────────────────
        queryset = self.filter_queryset(queryset)

        # ── 5. Paginate ──────────────────────────────────
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(
                serializer.data,
            )

        # ── 6. Serialize and return ──────────────────────
        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# MONTHLY ATTENDANCE SUMMARY
# ==========================================================

class MonthlyAttendanceSummaryAPIView(
    BaseAttendanceReportAPIView,
):
    """
    GET /api/attendance/reports/monthly/

    Returns aggregated attendance totals per employee
    for a given month and year.

    Query Parameters
    ----------------
    month : int, required
        Month number (1-12).

    year : int, required
        Four-digit year.

    Example
    -------
    GET /api/attendance/reports/monthly/?month=6&year=2026
    GET /api/attendance/reports/monthly/?month=1&year=2026
    """

    serializer_class = MonthlyAttendanceSummarySerializer

    def get(self, request, *args, **kwargs):

        # ── 1. Validate month and year ───────────────────
        month_param = request.query_params.get("month")
        year_param = request.query_params.get("year")

        if not month_param or not year_param:
            return Response(
                {
                    "error": (
                        "Both month and year "
                        "are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            month = int(month_param)
            year = int(year_param)
        except ValueError:
            return Response(
                {
                    "error": (
                        "month and year must be integers."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not 1 <= month <= 12:
            return Response(
                {
                    "error": (
                        "month must be between 1 and 12."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not 2000 <= year <= 2100:
            return Response(
                {
                    "error": (
                        "year must be between 2000 and 2100."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── 2. Call service ──────────────────────────────
        service = self.get_service()
        results = service.monthly_summary(
            month=month,
            year=year,
        )

        # ── 3. Serialize ─────────────────────────────────
        # monthly_summary returns a QuerySet with
        # annotated values. We serialize each row.
        serializer = self.get_serializer(
            results,
            many=True,
        )

        return Response(
            {
                "month": month,
                "year": year,
                "count": len(serializer.data),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ATTENDANCE DASHBOARD
# ==========================================================

class AttendanceDashboardAPIView(
    BaseAttendanceReportAPIView,
):
    """
    GET /api/attendance/reports/dashboard/

    Returns today's high-level attendance KPIs.

    No pagination needed — returns a single dict.

    Query Parameters
    ----------------
    date : YYYY-MM-DD, optional
        Dashboard date. Defaults to today.

    Example
    -------
    GET /api/attendance/reports/dashboard/
    GET /api/attendance/reports/dashboard/?date=2026-06-27
    """

    serializer_class = AttendanceDashboardSerializer

    def get(self, request, *args, **kwargs):

        # ── 1. Parse date parameter ──────────────────────
        date_param = request.query_params.get("date")

        if date_param:
            try:
                dashboard_date = date.fromisoformat(
                    date_param,
                )
            except ValueError:
                return Response(
                    {
                        "error": (
                            "Invalid date format. "
                            "Use YYYY-MM-DD."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            dashboard_date = None

        # ── 2. Call service ──────────────────────────────
        service = self.get_service()
        data = service.dashboard(
            dashboard_date=dashboard_date,
        )

        # ── 3. Serialize and return ──────────────────────
        # No pagination — dashboard returns one dict.
        serializer = self.get_serializer(data)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# ATTENDANCE EXCEPTIONS REPORT
# ==========================================================

class AttendanceExceptionAPIView(
    BaseAttendanceReportAPIView,
):
    """
    GET /api/attendance/reports/exceptions/

    Returns attendance records with anomalies
    flagged for HR review.

    Each record includes exception_types — a list
    of reasons why it was flagged.

    Query Parameters
    ----------------
    date_from : YYYY-MM-DD, optional
        Start of date range. Defaults to today.

    date_to : YYYY-MM-DD, optional
        End of date range. Defaults to today.

    Example
    -------
    GET /api/attendance/reports/exceptions/
    GET /api/attendance/reports/exceptions/?date_from=2026-06-01&date_to=2026-06-30
    """

    serializer_class = AttendanceExceptionSerializer

    def get(self, request, *args, **kwargs):

        # ── 1. Parse date range ──────────────────────────
        date_from_param = request.query_params.get(
            "date_from",
        )
        date_to_param = request.query_params.get(
            "date_to",
        )

        try:
            date_from = (
                date.fromisoformat(date_from_param)
                if date_from_param else None
            )
            date_to = (
                date.fromisoformat(date_to_param)
                if date_to_param else None
            )
        except ValueError:
            return Response(
                {
                    "error": (
                        "Invalid date format. "
                        "Use YYYY-MM-DD."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── 2. Call service ──────────────────────────────
        service = self.get_service()
        results = service.exceptions(
            date_from=date_from,
            date_to=date_to,
        )

        # ── 3. Build response ────────────────────────────
        # exceptions() returns a list of dicts
        # Each dict has "record" and "exception_types"
        # We serialize "record" and attach "exception_types"
        response_data = []

        for item in results:
            serialized = self.get_serializer(
                item["record"],
            ).data
            serialized["exception_types"] = (
                item["exception_types"]
            )
            response_data.append(serialized)

        # ── 4. Paginate ──────────────────────────────────
        page = self.paginate_queryset(response_data)

        if page is not None:
            return self.get_paginated_response(page)

        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )