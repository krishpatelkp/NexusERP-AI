from django.urls import path

from .views import (
    HolidayListCreateAPIView,
    HolidayRetrieveUpdateDestroyAPIView,
    CheckInAPIView,
    CheckOutAPIView,
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

]