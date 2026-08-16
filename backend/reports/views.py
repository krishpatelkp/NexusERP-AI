from datetime import datetime

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.report_serializers import EmployeeAttendanceHistorySerializer

from .serializers import (
    EmployeeSummarySerializer,
    EmployeeRegisterSerializer,
    EmployeeTrendSerializer,
    AttendanceSummarySerializer,
    MonthlyAttendanceSummarySerializer,
    DepartmentAttendanceSerializer,
    AttendanceTrendSerializer,
    AttendanceDashboardSerializer,
    AttendanceExceptionSerializer,
    DailyAttendanceSerializer,

    TopAbsenteesSerializer,
    BestAttendanceSerializer,
    LeaveSummarySerializer,
    LeaveBalanceReportSerializer,
    LeaveHistorySerializer,
    DepartmentLeaveSummarySerializer,
    LeaveTrendSerializer,
    PayrollSummarySerializer,
    PayrollRegisterSerializer,
    DepartmentSalaryCostSerializer,
    PayrollTrendSerializer,
    HighestEarnersSerializer,
    InventorySummarySerializer,
    AssetRegisterSerializer,
    AssignedAssetSerializer,
    MaintenanceHistorySerializer,
    MaintenanceTrendSerializer,
    MostMaintainedAssetSerializer,
    VendorAssetSerializer,
    PaymentSummarySerializer,
    PaymentRegisterSerializer,
    PaymentTrendSerializer,
)
from .services import (
    EmployeeReportService,
    LeaveReportService,
    PayrollReportService,
    InventoryReportService,
    PaymentReportService,
    AttendanceReportService,
)


from attendance.reports import AttendanceReportService as DetailedAttendanceReportService

# ==========================================================
# BASE REPORT API VIEW
# ==========================================================

class BaseReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    service_class = None

    def get_service(self):

        if self.service_class is None:
            raise NotImplementedError(
                "service_class must be defined."
            )

        return self.service_class(
            company=self.request.user.employee_profile.company,
        )

    def get_date(
        self,
        key,
        required=False,
    ):
        """
        Reads a date query parameter and returns a date object.

        Raises ValidationError (HTTP 400) if required and missing,
        or if the format is invalid.

        Example:
            ?date=2026-07-01
        """

        value = self.request.query_params.get(key)

        if not value:
            if required:
                raise ValidationError(
                    {key: f"{key} query parameter is required."}
                )
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError(
                {key: f"Invalid date format for '{key}'. Expected YYYY-MM-DD."}
            )

    def get_month(self):
        """
        Reads the 'month' query parameter (1-12).
        Raises ValidationError (HTTP 400) if missing or invalid.
        """

        value = self.request.query_params.get("month")

        if value is None:
            raise ValidationError(
                {"month": "month query parameter is required."}
            )

        try:
            month = int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                {"month": "month must be an integer between 1 and 12."}
            )

        if not 1 <= month <= 12:
            raise ValidationError(
                {"month": "month must be between 1 and 12."}
            )

        return month

    def get_year(self):
        """
        Reads the 'year' query parameter.
        Raises ValidationError (HTTP 400) if missing or invalid.
        """

        value = self.request.query_params.get("year")

        if value is None:
            raise ValidationError(
                {"year": "year query parameter is required."}
            )

        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                {"year": "year must be a valid integer."}
            )


# ==========================================================
# EMPLOYEE SUMMARY REPORT
# ==========================================================

class EmployeeSummaryAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.employee_summary()

        serializer = EmployeeSummarySerializer(
            data,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    


# ==========================================================
# EMPLOYEE REGISTER REPORT
# ==========================================================

class EmployeeRegisterAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.employee_register()

        serializer = EmployeeRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# EMPLOYEES BY DEPARTMENT REPORT
# ==========================================================

class EmployeesByDepartmentAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.employees_by_department()

        serializer = EmployeeRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# EMPLOYEES BY DESIGNATION REPORT
# ==========================================================

class EmployeesByDesignationAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.employees_by_designation()

        serializer = EmployeeRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# EMPLOYEES BY STATUS REPORT
# ==========================================================

class EmployeesByStatusAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.employees_by_status()

        serializer = EmployeeRegisterSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    


# ==========================================================
# EMPLOYEE JOINING REPORT
# ==========================================================

class JoiningReportAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(
        self,
        request,
    ):

        date_from = self.get_date(
            "date_from",
        )

        date_to = self.get_date(
            "date_to",
        )

        service = self.get_service()

        queryset = service.joining_report(
            date_from=date_from,
            date_to=date_to,
        )

        serializer = EmployeeRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# EMPLOYEE RESIGNATION REPORT
# ==========================================================

class ResignationReportAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(
        self,
        request,
    ):

        date_from = self.get_date(
            "date_from",
        )

        date_to = self.get_date(
            "date_to",
        )

        service = self.get_service()

        queryset = service.resignation_report(
            date_from=date_from,
            date_to=date_to,
        )

        serializer = EmployeeRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# HEADCOUNT TREND REPORT
# ==========================================================

class HeadcountTrendAPIView(
    BaseReportAPIView,
):

    service_class = EmployeeReportService

    def get(self, request):
        year = request.query_params.get("year")
        year = int(year) if year else None

        service = self.get_service()
        data = service.headcount_trend(year=year)

        serializer = EmployeeTrendSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# ==========================================================
# ATTENDANCE SUMMARY REPORT
# ==========================================================

class AttendanceSummaryAPIView(
    BaseReportAPIView,
):

    service_class = AttendanceReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.attendance_summary()

        serializer = AttendanceSummarySerializer(
            data,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    


# ==========================================================
# DAILY ATTENDANCE REPORT
# ==========================================================

class DailyAttendanceAPIView(
    BaseReportAPIView,
):

    service_class = DetailedAttendanceReportService

    def get(
        self,
        request,
    ):

        date = self.get_date(
            "date",
        )

        service = self.get_service()

        queryset = service.daily_report(
            report_date=date,
        )

        serializer = DailyAttendanceSerializer(
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
    BaseReportAPIView,
):

    service_class = DetailedAttendanceReportService

    def get(
        self,
        request,
        employee_id,
    ):

        date_from = self.get_date(
            "date_from",
            required=False,
        )

        date_to = self.get_date(
            "date_to",
            required=False,
        )

        service = self.get_service()

        queryset = service.employee_history(
            employee_id=employee_id,
            date_from=date_from,
            date_to=date_to,
        )

        serializer = EmployeeAttendanceHistorySerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# MONTHLY ATTENDANCE REPORT
# ==========================================================

class MonthlyAttendanceAPIView(
    BaseReportAPIView,
):

    service_class = DetailedAttendanceReportService

    def get(
        self,
        request,
    ):

        month = self.get_month()

        year = self.get_year()

        service = self.get_service()

        data = service.monthly_summary(
            month=month,
            year=year,
        )

        serializer = MonthlyAttendanceSummarySerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    


# ==========================================================
# DEPARTMENT ATTENDANCE SUMMARY
# ==========================================================

class DepartmentAttendanceAPIView(
    BaseReportAPIView,
):

    service_class = AttendanceReportService

    def get(
        self,
        request,
    ):

        month = self.get_month()

        year = self.get_year()

        service = self.get_service()

        data = service.department_attendance_summary(
            month=month,
            year=year,
        )

        serializer = DepartmentAttendanceSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# ATTENDANCE DASHBOARD
# ==========================================================

class AttendanceDashboardAPIView(
    BaseReportAPIView,
):

    service_class = DetailedAttendanceReportService

    def get(
        self,
        request,
    ):

        date = self.get_date(
            "date",
            required=False,
        )

        service = self.get_service()

        data = service.dashboard(
            dashboard_date=date,
        )

        serializer = AttendanceDashboardSerializer(
            data,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# ATTENDANCE TREND
# ==========================================================

class AttendanceTrendAPIView(
    BaseReportAPIView,
):

    service_class = AttendanceReportService

    def get(self, request):
        year = request.query_params.get("year")
        year = int(year) if year else None

        service = self.get_service()
        data = service.attendance_trend(year=year)

        serializer = AttendanceTrendSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# ==========================================================
# ATTENDANCE EXCEPTIONS
# ==========================================================

class AttendanceExceptionsAPIView(
    BaseReportAPIView,
):

    service_class = DetailedAttendanceReportService

    def get(
        self,
        request,
    ):

        date_from = self.get_date(
            "date_from",
        )

        date_to = self.get_date(
            "date_to",
        )

        service = self.get_service()

        queryset = service.exceptions(
            date_from=date_from,
            date_to=date_to,
        )

        serializer = AttendanceExceptionSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# TOP ABSENTEES
# ==========================================================

class TopAbsenteesAPIView(
    BaseReportAPIView,
):

    service_class = AttendanceReportService

    def get(
        self,
        request,
    ):

        limit = int(
            request.query_params.get(
                "limit",
                10,
            )
        )

        service = self.get_service()

        data = service.top_absentees(
            limit=limit,
        )

        serializer = TopAbsenteesSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# BEST ATTENDANCE
# ==========================================================

class BestAttendanceAPIView(
    BaseReportAPIView,
):

    service_class = AttendanceReportService

    def get(
        self,
        request,
    ):

        limit = int(
            request.query_params.get(
                "limit",
                10,
            )
        )

        service = self.get_service()

        data = service.best_attendance(
            limit=limit,
        )

        serializer = BestAttendanceSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# LEAVE SUMMARY REPORT
# ==========================================================

class LeaveSummaryAPIView(
    BaseReportAPIView,
):

    service_class = LeaveReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.leave_summary()

        serializer = LeaveSummarySerializer(
            data,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# LEAVE BALANCE REPORT
# ==========================================================

class LeaveBalanceAPIView(
    BaseReportAPIView,
):

    service_class = LeaveReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.leave_balance_report()

        serializer = LeaveBalanceReportSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# LEAVE HISTORY REPORT
# ==========================================================

class LeaveHistoryAPIView(
    BaseReportAPIView,
):

    service_class = LeaveReportService

    def get(
        self,
        request,
    ):

        employee_id = request.query_params.get(
            "employee_id",
        )

        service = self.get_service()

        queryset = service.leave_history(
            employee_id=employee_id,
        )

        serializer = LeaveHistorySerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# DEPARTMENT LEAVE SUMMARY
# ==========================================================

class DepartmentLeaveSummaryAPIView(
    BaseReportAPIView,
):

    service_class = LeaveReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.department_leave_summary()

        serializer = DepartmentLeaveSummarySerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# LEAVE TREND REPORT
# ==========================================================

class LeaveTrendAPIView(
    BaseReportAPIView,
):

    service_class = LeaveReportService

    def get(self, request):
        year = request.query_params.get("year")
        year = int(year) if year else None

        service = self.get_service()
        data = service.leave_trend(year=year)

        serializer = LeaveTrendSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# ==========================================================
# PAYROLL SUMMARY REPORT
# ==========================================================

class PayrollSummaryAPIView(
    BaseReportAPIView,
):

    service_class = PayrollReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.payroll_summary()

        serializer = PayrollSummarySerializer(
            data,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# PAYROLL REGISTER REPORT
# ==========================================================

class PayrollRegisterAPIView(
    BaseReportAPIView,
):

    service_class = PayrollReportService

    def get(
        self,
        request,
    ):

        month = self.get_month()

        year = self.get_year()

        service = self.get_service()

        queryset = service.payroll_register(
            month=month,
            year=year,
        )

        serializer = PayrollRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# DEPARTMENT SALARY COST REPORT
# ==========================================================

class DepartmentSalaryCostAPIView(
    BaseReportAPIView,
):

    service_class = PayrollReportService

    def get(
        self,
        request,
    ):

        month = self.get_month()

        year = self.get_year()

        service = self.get_service()

        data = service.department_salary_cost(
            month=month,
            year=year,
        )

        serializer = DepartmentSalaryCostSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# PAYROLL TREND REPORT
# ==========================================================

class PayrollTrendAPIView(
    BaseReportAPIView,
):

    service_class = PayrollReportService

    def get(self, request):
        year = request.query_params.get("year")
        year = int(year) if year else None

        service = self.get_service()
        data = service.payroll_trend(year=year)

        serializer = PayrollTrendSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    

# ==========================================================
# HIGHEST EARNERS REPORT
# ==========================================================

class HighestEarnersAPIView(
    BaseReportAPIView,
):

    service_class = PayrollReportService

    def get(
        self,
        request,
    ):

        limit = int(
            request.query_params.get(
                "limit",
                10,
            )
        )

        service = self.get_service()

        data = service.highest_earners(
            limit=limit,
        )

        serializer = HighestEarnersSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# INVENTORY SUMMARY REPORT
# ==========================================================

class InventorySummaryAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.inventory_summary()

        serializer = InventorySummarySerializer(
            data,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    
# ==========================================================
# ASSET REGISTER REPORT
# ==========================================================

class AssetRegisterAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.asset_register()

        serializer = AssetRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# ASSIGNED ASSETS REPORT
# ==========================================================

class AssignedAssetsAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.assigned_assets()

        serializer = AssignedAssetSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# MAINTENANCE HISTORY REPORT
# ==========================================================

class MaintenanceHistoryAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.maintenance_history()

        serializer = MaintenanceHistorySerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# RETIRED ASSETS REPORT
# ==========================================================

class RetiredAssetsAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.retired_assets()

        serializer = AssetRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# MAINTENANCE COST TREND REPORT
# ==========================================================

class MaintenanceTrendAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        year = self.get_year()

        service = self.get_service()

        data = service.maintenance_cost_trend(
            year=year,
        )

        serializer = MaintenanceTrendSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# MOST MAINTAINED ASSETS REPORT
# ==========================================================

class MostMaintainedAssetsAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        limit = int(
            request.query_params.get(
                "limit",
                10,
            )
        )

        service = self.get_service()

        data = service.most_maintained_assets(
            limit=limit,
        )

        serializer = MostMaintainedAssetSerializer(
            data,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# ASSETS BY VENDOR REPORT
# ==========================================================

class VendorAssetsAPIView(
    BaseReportAPIView,
):

    service_class = InventoryReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.assets_by_vendor()

        serializer = VendorAssetSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# PAYMENT SUMMARY REPORT
# ==========================================================

class PaymentSummaryAPIView(
    BaseReportAPIView,
):

    service_class = PaymentReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        data = service.payment_summary()

        serializer = PaymentSummarySerializer(
            data,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# PAYMENT REGISTER REPORT
# ==========================================================

class PaymentRegisterAPIView(
    BaseReportAPIView,
):

    service_class = PaymentReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.payment_register()

        serializer = PaymentRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# PENDING PAYMENTS REPORT
# ==========================================================

class PendingPaymentsAPIView(
    BaseReportAPIView,
):

    service_class = PaymentReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.pending_payments()

        serializer = PaymentRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# FAILED PAYMENTS REPORT
# ==========================================================

class FailedPaymentsAPIView(
    BaseReportAPIView,
):

    service_class = PaymentReportService

    def get(
        self,
        request,
    ):

        service = self.get_service()

        queryset = service.failed_payments()

        serializer = PaymentRegisterSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# PAYMENT TREND REPORT
# ==========================================================

class PaymentTrendAPIView(
    BaseReportAPIView,
):

    service_class = PaymentReportService

    def get(self, request):
        year = request.query_params.get("year")
        year = int(year) if year else None

        service = self.get_service()
        data = service.payment_trend(year=year)

        serializer = PaymentTrendSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
