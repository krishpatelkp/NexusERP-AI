from django.urls import path

from .views import (
    HolidayListCreateAPIView,
    HolidayRetrieveUpdateDestroyAPIView,
)

urlpatterns = [

    # ======================================================
    # HOLIDAY APIs
    # ======================================================

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

]