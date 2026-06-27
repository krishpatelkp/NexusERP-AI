from django.urls import path

from .views import (
    HolidayListCreateAPIView,
    HolidayRetrieveUpdateDestroyAPIView,
    CheckInAPIView,
    CheckOutAPIView,
)

from .report_views import (
    DailyAttendanceReportAPIView,
    EmployeeAttendanceHistoryAPIView,
    MonthlyAttendanceSummaryAPIView,
    AttendanceDashboardAPIView,
    AttendanceExceptionAPIView,
)


urlpatterns = [

    # ==========================
    # Holiday
    # ==========================

    path(
        "holidays/",
        HolidayListCreateAPIView.as_view(),
        name="holiday-list-create",
    ),

    path(
        "holidays/<int:pk>/",
        HolidayRetrieveUpdateDestroyAPIView.as_view(),
        name="holiday-detail",
    ),

    # ==========================
    # Attendance
    # ==========================

    path(
        "check-in/",
        CheckInAPIView.as_view(),
        name="check-in",
    ),

    path(
        "check-out/",
        CheckOutAPIView.as_view(),
        name="check-out",
    ),

    # ==========================
    # Reports
    # ==========================

    path(
        "reports/daily/",
        DailyAttendanceReportAPIView.as_view(),
        name="report-daily",
    ),

    path(
        "reports/employee/",
        EmployeeAttendanceHistoryAPIView.as_view(),
        name="report-employee-history",
    ),

    path(
        "reports/monthly/",
        MonthlyAttendanceSummaryAPIView.as_view(),
        name="report-monthly",
    ),

    path(
        "reports/dashboard/",
        AttendanceDashboardAPIView.as_view(),
        name="report-dashboard",
    ),

    path(
        "reports/exceptions/",
        AttendanceExceptionAPIView.as_view(),
        name="report-exceptions",
    ),

]