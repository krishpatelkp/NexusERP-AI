from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import (
    generics,
    permissions,
    status,
)

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import (
    LeaveBalance,
    LeaveRequest,
    LeaveType,
)
from employees.models import Employee

from .serializers import (
    LeaveBalanceSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestDetailSerializer,
    LeaveTypeSerializer,
    ApproveLeaveSerializer,
    RejectLeaveSerializer,
    CancelLeaveSerializer,
)

from .services import LeaveService
from .pagination import LeavePagination


# ==========================================================
# HELPER — converts Django ValidationError → DRF 400
# ==========================================================

def _raise_drf(exc):
    """
    Convert django.core.exceptions.ValidationError
    into a DRF ValidationError so the API returns
    HTTP 400 instead of 500.
    """
    raise DRFValidationError(
        detail=exc.message_dict
        if hasattr(exc, "message_dict")
        else exc.messages,
    )


# ==========================================================
# APPLY LEAVE API
# ==========================================================

class LeaveRequestCreateAPIView(
    generics.GenericAPIView,
):
    """
    Apply for leave.
    """

    serializer_class = (
        LeaveRequestCreateSerializer
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        employee = getattr(request.user, "employee_profile", None) or Employee.objects.filter(is_active=True).first()

        if not employee:
            return Response(
                {"error": "No active employee profile found to apply for leave."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = LeaveService(
            employee=employee,
        )

        try:
            leave_request = service.apply_leave(
                leave_type=serializer.validated_data["leave_type"],
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
                is_half_day=serializer.validated_data.get("is_half_day", False),
                reason=serializer.validated_data.get("reason", ""),
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message":
                "Leave request submitted successfully.",

                "leave_request":
                LeaveRequestDetailSerializer(
                    leave_request,
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )
    

# ==========================================================
# EMPLOYEE LEAVE REQUEST LIST API
# ==========================================================

class LeaveRequestListAPIView(
    generics.ListAPIView,
):
    """
    List all leave requests
    of the logged-in employee.
    """

    serializer_class = (
        LeaveRequestDetailSerializer
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )

    pagination_class = (
        LeavePagination
    )

    def get_queryset(self):
        user = self.request.user
        role_name = (getattr(user.role, "role_name", "") if hasattr(user, "role") and user.role else "").upper()
        is_admin_or_hr = user.is_superuser or user.is_staff or any(
            keyword in role_name for keyword in ["ADMIN", "HR", "MANAGER", "EXECUTIVE"]
        )

        qs = LeaveRequest.objects.select_related(
            "employee",
            "company",
            "leave_type",
            "approved_by",
        ).order_by("-created_at")

        if is_admin_or_hr:
            if user.is_superuser or not user.company:
                return qs
            return qs.filter(company=user.company)

        emp_profile = getattr(user, "employee_profile", None)
        if emp_profile:
            return qs.filter(employee=emp_profile)
        if user.company:
            return qs.filter(company=user.company)
        return qs.none()
    

# ==========================================================
# LEAVE REQUEST DETAIL API
# ==========================================================

class LeaveRequestRetrieveAPIView(
    generics.RetrieveAPIView,
):
    """
    Retrieve details of a leave request.
    """

    serializer_class = (
        LeaveRequestDetailSerializer
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        user = self.request.user
        role_name = (getattr(user.role, "role_name", "") if hasattr(user, "role") and user.role else "").upper()
        is_admin_or_hr = user.is_superuser or user.is_staff or any(
            keyword in role_name for keyword in ["ADMIN", "HR", "MANAGER", "EXECUTIVE"]
        )

        qs = LeaveRequest.objects.select_related(
            "employee",
            "company",
            "leave_type",
            "approved_by",
        )

        if is_admin_or_hr:
            if user.is_superuser or not user.company:
                return qs
            return qs.filter(company=user.company)

        emp_profile = getattr(user, "employee_profile", None)
        if emp_profile:
            return qs.filter(employee=emp_profile)
        return qs.none()
    

# ==========================================================
# APPROVE LEAVE API
# ==========================================================

class ApproveLeaveAPIView(
    generics.GenericAPIView,
):
    """
    Approve a leave request.
    """

    serializer_class = (
        ApproveLeaveSerializer
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(
        self,
        request,
        pk,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        leave_request = get_object_or_404(
            LeaveRequest.objects.select_related(
                "employee",
                "leave_type",
                "company",
            ),
            pk=pk,
        )

        service = LeaveService(
            employee=leave_request.employee,
        )

        try:
            leave_request = service.approve_leave(
                leave_request=leave_request,
                approved_by=request.user,
                approval_reason=serializer.validated_data[
                    "approval_reason"
                ],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message":
                "Leave request approved successfully.",

                "leave_request":
                LeaveRequestDetailSerializer(
                    leave_request,
                ).data,
            },
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# REJECT LEAVE API
# ==========================================================

class RejectLeaveAPIView(
    generics.GenericAPIView,
):
    """
    Reject a leave request.
    """

    serializer_class = (
        RejectLeaveSerializer
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(
        self,
        request,
        pk,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        leave_request = get_object_or_404(
            LeaveRequest.objects.select_related(
                "employee",
                "leave_type",
                "company",
            ),
            pk=pk,
        )

        service = LeaveService(
            employee=leave_request.employee,
        )

        try:
            leave_request = service.reject_leave(
                leave_request=leave_request,
                approved_by=request.user,
                approval_reason=serializer.validated_data[
                    "approval_reason"
                ],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message":
                "Leave request rejected successfully.",
                "leave_request":
                LeaveRequestDetailSerializer(
                    leave_request,
                ).data,
            },
            status=status.HTTP_200_OK,
        )
    

# ==========================================================
# CANCEL LEAVE API
# ==========================================================

class CancelLeaveAPIView(
    generics.GenericAPIView,
):
    """
    Cancel a leave request.
    """

    serializer_class = (
        CancelLeaveSerializer
    )

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def post(
        self,
        request,
        pk,
        *args,
        **kwargs,
    ):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        leave_request = get_object_or_404(
            LeaveRequest.objects.select_related(
                "employee",
                "leave_type",
                "company",
            ),
            pk=pk,
        )

        service = LeaveService(
            employee=leave_request.employee,
        )

        try:
            leave_request = service.cancel_leave(
                leave_request=leave_request,
                remarks=serializer.validated_data[
                    "remarks"
                ],
            )
        except DjangoValidationError as exc:
            _raise_drf(exc)

        return Response(
            {
                "message":
                "Leave request cancelled successfully.",

                "leave_request":
                LeaveRequestDetailSerializer(
                    leave_request,
                ).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# LEAVE TYPE LIST API
# ==========================================================

class LeaveTypeListAPIView(generics.ListAPIView):
    """
    List active leave policies.
    """
    serializer_class = LeaveTypeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        qs = LeaveType.objects.filter(is_active=True)
        if user.company:
            comp_qs = qs.filter(Q(company=user.company) | Q(company__isnull=True))
            if comp_qs.exists():
                return comp_qs
        return qs


# ==========================================================
# LEAVE BALANCE LIST API
# ==========================================================

class LeaveBalanceListAPIView(generics.ListAPIView):
    """
    List employee leave balances.
    """
    serializer_class = LeaveBalanceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        role_name = (getattr(user.role, "role_name", "") if hasattr(user, "role") and user.role else "").upper()
        is_admin_or_hr = user.is_superuser or user.is_staff or any(
            keyword in role_name for keyword in ["ADMIN", "HR", "MANAGER", "EXECUTIVE"]
        )

        qs = LeaveBalance.objects.select_related(
            "employee",
            "leave_type",
            "company",
        ).order_by("-year", "leave_type__leave_name")

        if is_admin_or_hr:
            if user.is_superuser or not user.company:
                return qs
            return qs.filter(company=user.company)

        emp_profile = getattr(user, "employee_profile", None)
        if emp_profile:
            return qs.filter(employee=emp_profile)
        if user.company:
            return qs.filter(company=user.company)
        return qs.none()