from django.shortcuts import render

from rest_framework import generics, permissions

from rest_framework.response import Response
from rest_framework import status

from .models import Holiday

from .serializers import (
    HolidaySerializer,
    CheckInSerializer,
    CheckOutSerializer,
    AttendanceSerializer,
)

from .services import (
    AttendanceCalculationService,
)

from core.utils import get_user_company


# Create your views here.

# ==========================================================
# HOLIDAY LIST & CREATE
# ==========================================================

class HolidayListCreateAPIView(
    generics.ListCreateAPIView,
):
    """
    List all active holidays
    or create a new holiday.
    """

    serializer_class = HolidaySerializer

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        user = self.request.user
        company = get_user_company(user)
        if company:
            return Holiday.objects.select_related(
                "company",
            ).filter(
                company=company,
                is_active=True,
            )

        if user.is_superuser:
            return Holiday.objects.select_related(
                "company",
            ).filter(
                is_active=True,
            )

        return Holiday.objects.none()

    def perform_create(self, serializer):
        company = get_user_company(self.request.user)
        if company:
            serializer.save(company=company)
        else:
            serializer.save()
    

# ==========================================================
# HOLIDAY DETAIL
# ==========================================================

class HolidayRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    Retrieve,
    update,
    or soft delete a holiday.
    """

    serializer_class = HolidaySerializer

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        user = self.request.user
        company = get_user_company(user)
        if company:
            return Holiday.objects.select_related(
                "company",
            ).filter(
                company=company,
            )

        if user.is_superuser:
            return Holiday.objects.select_related(
                "company",
            )

        return Holiday.objects.none()

    def perform_destroy(
        self,
        instance,
    ):
        """
        Soft delete.
        """

        instance.is_active = False

        instance.save(
            update_fields=[
                "is_active",
            ]
        )

    
# ==========================================================
# CHECK-IN API
# ==========================================================

class CheckInAPIView(
    generics.GenericAPIView,
):
    """
    Employee Check-In API.
    """

    serializer_class = CheckInSerializer

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

        company = get_user_company(request.user)
        employee = (
            serializer.validated_data.get("employee")
            or getattr(request.user, "employee_profile", None)
            or (Employee.objects.filter(company=company, is_active=True).first() if company else None)
        )

        if not employee:
            return Response(
                {"error": "No active employee profile found in this company to record attendance."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AttendanceCalculationService(
            employee=employee,
        )

        attendance = service.process_check_in(
            check_in=serializer.validated_data["check_in"],
            remarks=serializer.validated_data.get("remarks", ""),
        )

        return Response(
            {
                "message": "Check-in successful.",
                "attendance": AttendanceSerializer(attendance).data,
            },
            status=status.HTTP_200_OK,
        )
    
# ==========================================================
# CHECK-OUT API
# ==========================================================

class CheckOutAPIView(
    generics.GenericAPIView,
):
    """
    Employee Check-Out API.
    """

    serializer_class = CheckOutSerializer

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

        company = get_user_company(request.user)
        employee = (
            serializer.validated_data.get("employee")
            or getattr(request.user, "employee_profile", None)
            or (Employee.objects.filter(company=company, is_active=True).first() if company else None)
        )

        if not employee:
            return Response(
                {"error": "No active employee profile found in this company to record attendance."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AttendanceCalculationService(
            employee=employee,
        )

        attendance = service.process_check_out(
            check_out=serializer.validated_data["check_out"],
            remarks=serializer.validated_data.get("remarks", ""),
        )

        return Response(
            {
                "message": "Check-out successful.",
                "attendance_id": AttendanceSerializer(attendance).data,
            },
            status=status.HTTP_200_OK,
        )