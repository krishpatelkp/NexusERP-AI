from django.shortcuts import render

from rest_framework import generics, permissions

from .models import Holiday
from .serializers import HolidaySerializer

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