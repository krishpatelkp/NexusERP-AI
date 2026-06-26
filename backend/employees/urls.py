from django.urls import path

from .views import (
    DepartmentListCreateAPIView,
    DepartmentRetrieveUpdateDestroyAPIView,
    DesignationListCreateAPIView,
    DesignationRetrieveUpdateDestroyAPIView,
    EmployeeListCreateAPIView,
    EmployeeRetrieveUpdateDestroyAPIView,
    EmployeeAddressListCreateAPIView,
    EmployeeAddressRetrieveUpdateDestroyAPIView,
    EmergencyContactListCreateAPIView,
    EmergencyContactRetrieveUpdateDestroyAPIView,
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

    # ==========================================================
    # EMPLOYEE URLS
    # ==========================================================

    path(
        "employees/",
        EmployeeListCreateAPIView.as_view(),
        name="employee-list-create",
    ),

    path(
        "employees/<int:pk>/",
        EmployeeRetrieveUpdateDestroyAPIView.as_view(),
        name="employee-detail",
    ),


# ==========================================================
# EMPLOYEE ADDRESS URLS
# ==========================================================

    path(
        "employee-addresses/",
        EmployeeAddressListCreateAPIView.as_view(),
        name="employee-address-list-create",
    ),

    path(
        "employee-addresses/<int:pk>/",
        EmployeeAddressRetrieveUpdateDestroyAPIView.as_view(),
        name="employee-address-detail",
    ),
# ==========================================================
# EMERGENCY CONTACT URLS
# ==========================================================

    path(
        "emergency-contacts/",
        EmergencyContactListCreateAPIView.as_view(),
        name="emergency-contact-list-create",
    ),

    path(
        "emergency-contacts/<int:pk>/",
        EmergencyContactRetrieveUpdateDestroyAPIView.as_view(),
        name="emergency-contact-detail",
    ),

]


