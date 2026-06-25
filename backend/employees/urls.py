from django.urls import path

from .views import (
    DepartmentListCreateAPIView,
    DepartmentRetrieveUpdateDestroyAPIView,
    DesignationListCreateAPIView,
    DesignationRetrieveUpdateDestroyAPIView,
)


app_name = "employees"


urlpatterns = [

    # ==========================================================
    # DEPARTMENT URLS
    # ==========================================================

    path(
        "departments/",
        DepartmentListCreateAPIView.as_view(),
        name="department-list-create",
    ),

    path(
        "departments/<int:pk>/",
        DepartmentRetrieveUpdateDestroyAPIView.as_view(),
        name="department-detail",
    ),

    # ==========================================================
    # DESIGNATION URLS
    # ==========================================================

    path(
        "designations/",
        DesignationListCreateAPIView.as_view(),
        name="designation-list-create",
    ),

    path(
        "designations/<int:pk>/",
        DesignationRetrieveUpdateDestroyAPIView.as_view(),
        name="designation-detail",
    ),

]