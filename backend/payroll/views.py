from django.shortcuts import get_object_or_404
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)

from rest_framework import (
    generics,
    permissions,
    status,
)

from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)

from .models import (
    PayrollCycle,
    PayrollItem,
    PayrollRun,
    Payslip,
)

from .serializers import (
    CreatePayrollCycleSerializer,
    CreatePayrollRunSerializer,
    PayrollCycleSerializer,
    PayrollItemSerializer,
    PayrollRunSerializer,
    PayslipSerializer,
    RemarksSerializer,
)

from .services import PayrollService
from .pagination import PayrollPagination


# ==========================================================
# HELPER — Django ValidationError → DRF 400
# ==========================================================

def _raise_drf(exc):
    """
    Convert django.core.exceptions.ValidationError
    to a DRF 400 ValidationError.
    """
    raise DRFValidationError(
        detail=(
            exc.message_dict
            if hasattr(exc, "message_dict")
            else exc.messages
        )
    )


# ==========================================================
# PAYROLL CYCLE — CREATE
# ==========================================================

class PayrollCycleCreateAPIView(
    generics.GenericAPIView,
):
    """
    POST /api/payroll/cycles/
    Create a new payroll cycle.
    """

    serializer_class = CreatePayrollCycleSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        service = PayrollService(
            company=request.user.employee_profile.company,
            user=request.user,
        )

        try:
            cycle = service.create_payroll_cycle(
                month=serializer.validated_data["month"],
                year=serializer.validated_data["year"],
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
                total_working_days=serializer.validated_data[
                    "total_working_days"
                ],
                remarks=serializer.validated_data["remarks"],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message": "Payroll cycle created successfully.",
                "cycle": PayrollCycleSerializer(cycle).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# PAYROLL CYCLE — LIST
# ==========================================================

class PayrollCycleListAPIView(
    generics.ListAPIView,
):
    """
    GET /api/payroll/cycles/list/
    List all payroll cycles for the company.
    """

    serializer_class = PayrollCycleSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PayrollPagination

    def get_queryset(self):

        company = (
            self.request.user.employee_profile.company
        )

        return (
            PayrollCycle.objects
            .filter(company=company)
            .select_related("company", "created_by", "closed_by")
            .order_by("-year", "-month")
        )


# ==========================================================
# PAYROLL CYCLE — DETAIL
# ==========================================================

class PayrollCycleDetailAPIView(
    generics.RetrieveAPIView,
):
    """
    GET /api/payroll/cycles/<pk>/
    Retrieve a single payroll cycle.
    """

    serializer_class = PayrollCycleSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):

        company = (
            self.request.user.employee_profile.company
        )

        return PayrollCycle.objects.filter(
            company=company,
        ).select_related("company", "created_by", "closed_by")


# ==========================================================
# PAYROLL CYCLE — ACTIVATE
# ==========================================================

class PayrollCycleActivateAPIView(
    generics.GenericAPIView,
):
    """
    POST /api/payroll/cycles/<pk>/activate/
    Activate a Draft cycle.
    """

    serializer_class = RemarksSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cycle = get_object_or_404(
            PayrollCycle.objects.select_related("company"),
            pk=pk,
        )

        service = PayrollService(
            company=request.user.employee_profile.company,
            user=request.user,
        )

        try:
            cycle = service.activate_payroll_cycle(cycle=cycle)
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message": "Payroll cycle activated.",
                "cycle": PayrollCycleSerializer(cycle).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# PAYROLL RUN — CREATE
# ==========================================================

class PayrollRunCreateAPIView(
    generics.GenericAPIView,
):
    """
    POST /api/payroll/cycles/<pk>/runs/
    Create a payroll run inside an Active cycle.
    """

    serializer_class = CreatePayrollRunSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cycle = get_object_or_404(
            PayrollCycle.objects.select_related("company"),
            pk=pk,
        )

        service = PayrollService(
            company=request.user.employee_profile.company,
            user=request.user,
        )

        try:
            payroll_run = service.create_payroll_run(
                cycle=cycle,
                description=serializer.validated_data["description"],
                remarks=serializer.validated_data["remarks"],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message": "Payroll run created successfully.",
                "payroll_run": PayrollRunSerializer(payroll_run).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# PAYROLL RUN — LIST (all runs for a cycle)
# ==========================================================

class PayrollRunListAPIView(
    generics.ListAPIView,
):
    """
    GET /api/payroll/cycles/<pk>/runs/list/
    List all payroll runs for a cycle.
    """

    serializer_class = PayrollRunSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PayrollPagination

    def get_queryset(self):

        company = (
            self.request.user.employee_profile.company
        )

        cycle_pk = self.kwargs["pk"]

        return (
            PayrollRun.objects
            .filter(company=company, cycle__pk=cycle_pk)
            .select_related(
                "cycle",
                "created_by",
                "approved_by",
                "finalized_by",
            )
            .order_by("-created_at")
        )


# ==========================================================
# PAYROLL RUN — DETAIL
# ==========================================================

class PayrollRunDetailAPIView(
    generics.RetrieveAPIView,
):
    """
    GET /api/payroll/runs/<pk>/
    Retrieve a single payroll run.
    """

    serializer_class = PayrollRunSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):

        company = (
            self.request.user.employee_profile.company
        )

        return (
            PayrollRun.objects
            .filter(company=company)
            .select_related(
                "cycle",
                "created_by",
                "approved_by",
                "finalized_by",
            )
        )


# ==========================================================
# PAYROLL RUN — PROCESS
# ==========================================================

class PayrollRunProcessAPIView(
    generics.GenericAPIView,
):
    """
    POST /api/payroll/runs/<pk>/process/
    Process a Draft payroll run.
    Calculates salaries and generates payslips.
    """

    serializer_class = RemarksSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payroll_run = get_object_or_404(
            PayrollRun.objects.select_related(
                "cycle", "company",
            ),
            pk=pk,
        )

        service = PayrollService(
            company=request.user.employee_profile.company,
            user=request.user,
        )

        try:
            payroll_run = service.process_payroll_run(
                payroll_run=payroll_run,
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message": "Payroll processed successfully.",
                "payroll_run": PayrollRunSerializer(payroll_run).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# PAYROLL RUN — APPROVE
# ==========================================================

class PayrollRunApproveAPIView(
    generics.GenericAPIView,
):
    """
    POST /api/payroll/runs/<pk>/approve/
    Approve a Processed payroll run.
    """

    serializer_class = RemarksSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payroll_run = get_object_or_404(
            PayrollRun.objects.select_related("company"),
            pk=pk,
        )

        service = PayrollService(
            company=request.user.employee_profile.company,
            user=request.user,
        )

        try:
            payroll_run = service.approve_payroll_run(
                payroll_run=payroll_run,
                remarks=serializer.validated_data["remarks"],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message": "Payroll run approved.",
                "payroll_run": PayrollRunSerializer(payroll_run).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# PAYROLL RUN — FINALIZE
# ==========================================================

class PayrollRunFinalizeAPIView(
    generics.GenericAPIView,
):
    """
    POST /api/payroll/runs/<pk>/finalize/
    Finalize an Approved payroll run.
    Issues all payslips.
    """

    serializer_class = RemarksSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payroll_run = get_object_or_404(
            PayrollRun.objects.select_related("company"),
            pk=pk,
        )

        service = PayrollService(
            company=request.user.employee_profile.company,
            user=request.user,
        )

        try:
            payroll_run = service.finalize_payroll_run(
                payroll_run=payroll_run,
                remarks=serializer.validated_data["remarks"],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message": "Payroll run finalized. Payslips issued.",
                "payroll_run": PayrollRunSerializer(payroll_run).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# PAYROLL RUN — CANCEL
# ==========================================================

class PayrollRunCancelAPIView(
    generics.GenericAPIView,
):
    """
    POST /api/payroll/runs/<pk>/cancel/
    Cancel a payroll run.
    Deletes all items and payslips for this run.
    """

    serializer_class = RemarksSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payroll_run = get_object_or_404(
            PayrollRun.objects.select_related("company"),
            pk=pk,
        )

        service = PayrollService(
            company=request.user.employee_profile.company,
            user=request.user,
        )

        try:
            payroll_run = service.cancel_payroll_run(
                payroll_run=payroll_run,
                remarks=serializer.validated_data["remarks"],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message": "Payroll run cancelled.",
                "payroll_run": PayrollRunSerializer(payroll_run).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# PAYROLL ITEMS — LIST (for a run)
# ==========================================================

class PayrollItemListAPIView(
    generics.ListAPIView,
):
    """
    GET /api/payroll/runs/<pk>/items/
    List all payroll items for a run.
    """

    serializer_class = PayrollItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PayrollPagination

    def get_queryset(self):

        company = (
            self.request.user.employee_profile.company
        )

        run_pk = self.kwargs["pk"]

        return (
            PayrollItem.objects
            .filter(company=company, payroll_run__pk=run_pk)
            .select_related("employee", "component")
            .order_by("employee__employee_id", "display_order")
        )


# ==========================================================
# PAYSLIPS — LIST (for a run)
# ==========================================================

class PayslipListAPIView(
    generics.ListAPIView,
):
    """
    GET /api/payroll/runs/<pk>/payslips/
    List all payslips for a run.
    """

    serializer_class = PayslipSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PayrollPagination

    def get_queryset(self):

        company = (
            self.request.user.employee_profile.company
        )

        run_pk = self.kwargs["pk"]

        return (
            Payslip.objects
            .filter(company=company, payroll_run__pk=run_pk)
            .select_related(
                "employee",
                "payroll_run__cycle",
                "issued_by",
            )
            .order_by("employee__employee_id")
        )


# ==========================================================
# MY PAYSLIPS (employee self-service)
# ==========================================================

class MyPayslipListAPIView(
    generics.ListAPIView,
):
    """
    GET /api/payroll/my-payslips/
    Employee views their own payslips.
    """

    serializer_class = PayslipSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = PayrollPagination

    def get_queryset(self):

        employee = (
            self.request.user.employee_profile
        )

        return (
            Payslip.objects
            .filter(
                employee=employee,
                status__in=["Generated", "Issued"],
            )
            .select_related(
                "payroll_run__cycle",
                "issued_by",
            )
            .order_by("-created_at")
        )