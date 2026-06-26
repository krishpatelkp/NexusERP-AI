from django.shortcuts import render

from rest_framework import generics, permissions

from rest_framework.response import Response
from rest_framework import status

from .models import Holiday

from .serializers import (
    HolidaySerializer,
    CheckInSerializer,
    CheckOutSerializer,
)

from .services import (
    AttendanceCalculationService,
)

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

        if user.is_superuser:

            return Holiday.objects.select_related(
                "company",
            ).filter(
                is_active=True,
            )

        return Holiday.objects.select_related(
            "company",
        ).filter(
            company=user.company,
            is_active=True,
        )
    

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

        if user.is_superuser:

            return Holiday.objects.select_related(
                "company",
            )

        return Holiday.objects.select_related(
            "company",
        ).filter(
            company=user.company,
        )

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

        service = AttendanceCalculationService(
            employee=serializer.validated_data["employee"],
        )

        attendance = service.process_check_in(
            check_in=serializer.validated_data["check_in"],
            remarks=serializer.validated_data["remarks"],
        )

        return Response(
            {
                "message": "Check-in successful.",
                "attendance_id": AttendanceSerializer(attendance).data,
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

        service = AttendanceCalculationService(
            employee=serializer.validated_data["employee"],
        )

        attendance = service.process_check_out(
            check_out=serializer.validated_data["check_out"],
            remarks=serializer.validated_data["remarks"],
        )

        return Response(
            {
                "message": "Check-out successful.",
                "attendance_id": AttendanceSerializer(attendance).data,
            },
            status=status.HTTP_200_OK,
        )