from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


from accounts.permissions import (
    HasDepartmentCreatePermission,
    HasDepartmentViewPermission,
    HasDepartmentUpdatePermission,
    HasDepartmentDeletePermission,
    HasDesignationCreatePermission,
    HasDesignationViewPermission,
    HasDesignationUpdatePermission,
    HasDesignationDeletePermission,
)

from .models import (
    Department,
    Designation,
)

from .serializers import (
    DepartmentSerializer,
    DesignationSerializer,
)


# ─────────────────────────────────────────
# DEPARTMENT LIST & CREATE
# ─────────────────────────────────────────

class DepartmentListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    GET:
        Return a list of all active departments.

    POST:
        Create a new department.
    """

    serializer_class = DepartmentSerializer

    def get_queryset(self):
        """
        Return all active departments.
        Uses select_related() to reduce
        database queries when accessing company.
        """

        queryset = (
            Department.objects
            .select_related("company")
            .filter(is_active=True)
            .order_by("department_name")
        )

        if self.request.user.is_superuser:
            return queryset
        
        return queryset.filter(
            company=self.request.user.company
        )

    def get_permissions(self):
        """
        Assign permissions based on
        the current HTTP method.
        """

        if self.request.method == "POST":
            permission_classes = (
                IsAuthenticated,
                HasDepartmentCreatePermission,
            )
        else:
            permission_classes = (
                IsAuthenticated,
                HasDepartmentViewPermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]
    
    def perform_create(self, serializer):
        """
        Automatically set company from the
        logged-in user instead of trusting
        the client to send it.
        """
        serializer.save(company=self.request.user.company)


# ─────────────────────────────────────────
# DEPARTMENT DETAIL
# ─────────────────────────────────────────

class DepartmentRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    GET:
        Retrieve a single department.

    PUT/PATCH:
        Update a department.

    DELETE:
        Soft delete a department by
        marking it inactive.
    """

    serializer_class = DepartmentSerializer

    def get_queryset(self):
        """
        Return departments visible to the current user.
        Superusers can access all departments.
        Normal users can access only their company's departments.
        """
        queryset = (
            Department.objects
            .select_related("company")
            .filter(is_active=True)
            .order_by("department_name")
        )

        if self.request.user.is_superuser:
            return queryset
        
        return queryset.filter(
            company=self.request.user.company
        )
                    

    def get_permissions(self):
        """
        Assign permissions based on
        the current HTTP method.
        """

        if self.request.method == "GET":
            permission_classes = (
                IsAuthenticated,
                HasDepartmentViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):
            permission_classes = (
                IsAuthenticated,
                HasDepartmentUpdatePermission,
            )

        else:
            permission_classes = (
                IsAuthenticated,
                HasDepartmentDeletePermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_destroy(self, instance):
        """
        Soft delete the department.

        Instead of removing the record from
        the database, simply mark it inactive.
        """

        instance.is_active = False
        instance.save(update_fields=["is_active","updated_at"])


# ==========================================================
# DESIGNATION LIST & CREATE
# ==========================================================

class DesignationListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    GET:
        Return all active designations.

    POST:
        Create a new designation.
    """

    serializer_class = DesignationSerializer

    def get_queryset(self):

        queryset = (
            Designation.objects
            .select_related("company")
            .filter(is_active=True)
            .order_by("designation_name")
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            company=self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "POST":
            permission_classes = (
                IsAuthenticated,
                HasDesignationCreatePermission,
            )

        else:
            permission_classes = (
                IsAuthenticated,
                HasDesignationViewPermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]
    
    def perform_create(self, serializer):
        """
        Automatically set company from the
        logged-in user instead of trusting
        the client to send it.
        """
        serializer.save(company=self.request.user.company)


# ==========================================================
# DESIGNATION DETAIL
# ==========================================================

class DesignationRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update and soft delete a designation.
    """

    serializer_class = DesignationSerializer

    def get_queryset(self):

        queryset = (
            Designation.objects
            .select_related("company")
            .filter(is_active=True)
            .order_by("designation_name")
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            company=self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "GET":

            permission_classes = (
                IsAuthenticated,
                HasDesignationViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):

            permission_classes = (
                IsAuthenticated,
                HasDesignationUpdatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasDesignationDeletePermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_destroy(self, instance):
        """
        Soft delete the designation.
        """

        instance.is_active = False

        instance.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )