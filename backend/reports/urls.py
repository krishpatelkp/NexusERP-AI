from django.urls import path

from .views import (
    EmployeeSummaryAPIView,
    EmployeeRegisterAPIView,
    EmployeesByDepartmentAPIView,
    EmployeesByDesignationAPIView,
    EmployeesByStatusAPIView,
    JoiningReportAPIView,
    ResignationReportAPIView,
    HeadcountTrendAPIView,

    AttendanceSummaryAPIView,
    DailyAttendanceAPIView,
    EmployeeAttendanceHistoryAPIView,
    MonthlyAttendanceAPIView,
    DepartmentAttendanceAPIView,
    AttendanceDashboardAPIView,
    AttendanceTrendAPIView,
    AttendanceExceptionsAPIView,
    TopAbsenteesAPIView,
    BestAttendanceAPIView,

    LeaveSummaryAPIView,
    LeaveBalanceAPIView,
    LeaveHistoryAPIView,
    DepartmentLeaveSummaryAPIView,
    LeaveTrendAPIView,

    PayrollSummaryAPIView,
    PayrollRegisterAPIView,
    DepartmentSalaryCostAPIView,
    PayrollTrendAPIView,
    HighestEarnersAPIView,

    InventorySummaryAPIView,
    AssetRegisterAPIView,
    AssignedAssetsAPIView,
    MaintenanceHistoryAPIView,
    RetiredAssetsAPIView,
    MaintenanceTrendAPIView,
    MostMaintainedAssetsAPIView,
    VendorAssetsAPIView,

    PaymentSummaryAPIView,
    PaymentRegisterAPIView,
    PendingPaymentsAPIView,
    FailedPaymentsAPIView,
    PaymentTrendAPIView,
)


urlpatterns = [

    # ==========================================================
    # EMPLOYEE REPORTS
    # ==========================================================

    path(
        "employees/summary/",
        EmployeeSummaryAPIView.as_view(),
        name="employee-summary-report",
    ),

    path(
        "employees/register/",
        EmployeeRegisterAPIView.as_view(),
        name="employee-register-report",
    ),

    path(
        "employees/department/",
        EmployeesByDepartmentAPIView.as_view(),
        name="employees-by-department-report",
    ),

    path(
        "employees/designation/",
        EmployeesByDesignationAPIView.as_view(),
        name="employees-by-designation-report",
    ),

    path(
        "employees/status/",
        EmployeesByStatusAPIView.as_view(),
        name="employees-by-status-report",
    ),

    path(
        "employees/joinings/",
        JoiningReportAPIView.as_view(),
        name="employee-joining-report",
    ),

    path(
        "employees/resignations/",
        ResignationReportAPIView.as_view(),
        name="employee-resignation-report",
    ),

    path(
        "employees/trend/",
        HeadcountTrendAPIView.as_view(),
        name="employee-headcount-trend",
    ),


    # ==========================================================
    # ATTENDANCE REPORTS
    # ==========================================================

    path(
        "attendance/summary/",
        AttendanceSummaryAPIView.as_view(),
        name="attendance-summary-report",
    ),

    path(
        "attendance/daily/",
        DailyAttendanceAPIView.as_view(),
        name="daily-attendance-report",
    ),

    path(
        "attendance/history/<int:employee_id>/",
        EmployeeAttendanceHistoryAPIView.as_view(),
        name="employee-attendance-history",
    ),

    path(
        "attendance/monthly/",
        MonthlyAttendanceAPIView.as_view(),
        name="monthly-attendance-report",
    ),

    path(
        "attendance/department/",
        DepartmentAttendanceAPIView.as_view(),
        name="department-attendance-report",
    ),

    path(
        "attendance/dashboard/",
        AttendanceDashboardAPIView.as_view(),
        name="attendance-dashboard-report",
    ),

    path(
        "attendance/trend/",
        AttendanceTrendAPIView.as_view(),
        name="attendance-trend-report",
    ),

    path(
        "attendance/exceptions/",
        AttendanceExceptionsAPIView.as_view(),
        name="attendance-exceptions-report",
    ),

    path(
        "attendance/top-absentees/",
        TopAbsenteesAPIView.as_view(),
        name="top-absentees-report",
    ),

    path(
        "attendance/best/",
        BestAttendanceAPIView.as_view(),
        name="best-attendance-report",
    ),


    # ==========================================================
    # LEAVE REPORTS
    # ==========================================================

    path(
        "leave/summary/",
        LeaveSummaryAPIView.as_view(),
        name="leave-summary-report",
    ),

    path(
        "leave/balance/",
        LeaveBalanceAPIView.as_view(),
        name="leave-balance-report",
    ),

    path(
        "leave/history/",
        LeaveHistoryAPIView.as_view(),
        name="leave-history-report",
    ),

    path(
        "leave/department/",
        DepartmentLeaveSummaryAPIView.as_view(),
        name="department-leave-report",
    ),

    path(
        "leave/trend/",
        LeaveTrendAPIView.as_view(),
        name="leave-trend-report",
    ),

    # ==========================================================
    # PAYROLL REPORTS
    # ==========================================================

    path(
        "payroll/summary/",
        PayrollSummaryAPIView.as_view(),
        name="payroll-summary-report",
    ),

    path(
        "payroll/register/",
        PayrollRegisterAPIView.as_view(),
        name="payroll-register-report",
    ),

    path(
        "payroll/department-cost/",
        DepartmentSalaryCostAPIView.as_view(),
        name="department-salary-cost-report",
    ),

    path(
        "payroll/trend/",
        PayrollTrendAPIView.as_view(),
        name="payroll-trend-report",
    ),

    path(
        "payroll/highest-earners/",
        HighestEarnersAPIView.as_view(),
        name="highest-earners-report",
    ),


        # ==========================================================
    # INVENTORY REPORTS
    # ==========================================================

    path(
        "inventory/summary/",
        InventorySummaryAPIView.as_view(),
        name="inventory-summary-report",
    ),

    path(
        "inventory/assets/",
        AssetRegisterAPIView.as_view(),
        name="asset-register-report",
    ),

    path(
        "inventory/assigned/",
        AssignedAssetsAPIView.as_view(),
        name="assigned-assets-report",
    ),

    path(
        "inventory/maintenance/",
        MaintenanceHistoryAPIView.as_view(),
        name="maintenance-history-report",
    ),

    path(
        "inventory/retired/",
        RetiredAssetsAPIView.as_view(),
        name="retired-assets-report",
    ),

    path(
        "inventory/maintenance-trend/",
        MaintenanceTrendAPIView.as_view(),
        name="maintenance-trend-report",
    ),

    path(
        "inventory/most-maintained/",
        MostMaintainedAssetsAPIView.as_view(),
        name="most-maintained-assets-report",
    ),

    path(
        "inventory/vendors/",
        VendorAssetsAPIView.as_view(),
        name="vendor-assets-report",
    ),


        # ==========================================================
    # PAYMENT REPORTS
    # ==========================================================

    path(
        "payments/summary/",
        PaymentSummaryAPIView.as_view(),
        name="payment-summary-report",
    ),

    path(
        "payments/register/",
        PaymentRegisterAPIView.as_view(),
        name="payment-register-report",
    ),

    path(
        "payments/pending/",
        PendingPaymentsAPIView.as_view(),
        name="pending-payments-report",
    ),

    path(
        "payments/failed/",
        FailedPaymentsAPIView.as_view(),
        name="failed-payments-report",
    ),

    path(
        "payments/trend/",
        PaymentTrendAPIView.as_view(),
        name="payment-trend-report",
    ),

]