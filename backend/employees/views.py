from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)

from accounts.permissions import (
    HasDepartmentCreatePermission,
    HasDepartmentViewPermission,
    HasDepartmentUpdatePermission,
    HasDepartmentDeletePermission,
    HasDesignationCreatePermission,
    HasDesignationViewPermission,
    HasDesignationUpdatePermission,
    HasDesignationDeletePermission,
    HasEmployeeCreatePermission,
    HasEmployeeViewPermission,
    HasEmployeeUpdatePermission,
    HasEmployeeDeletePermission,
    HasEmployeeAddressCreatePermission,
    HasEmployeeAddressViewPermission,
    HasEmployeeAddressUpdatePermission,
    HasEmployeeAddressDeletePermission,
    HasEmergencyContactCreatePermission,
    HasEmergencyContactViewPermission,
    HasEmergencyContactUpdatePermission,
    HasEmergencyContactDeletePermission,
    HasEmployeeBankDetailCreatePermission,
    HasEmployeeBankDetailViewPermission,
    HasEmployeeBankDetailUpdatePermission,
    HasEmployeeBankDetailDeletePermission,
    HasEmployeeDocumentCreatePermission,
    HasEmployeeDocumentViewPermission,
    HasEmployeeDocumentUpdatePermission,
    HasEmployeeDocumentDeletePermission,
    HasShiftCreatePermission,
    HasShiftViewPermission,
    HasShiftUpdatePermission,
    HasShiftDeletePermission,
)

from .models import (
    Department,
    Designation,
    Employee,
    EmployeeAddress,
    EmergencyContact,  
    EmployeeBankDetail, 
    EmployeeDocument,
    Shift,
)

from .serializers import (
    DepartmentSerializer,
    DesignationSerializer,
    EmployeeSerializer,
    EmployeeAddressSerializer,
    EmergencyContactSerializer,
    EmployeeBankDetailSerializer, 
    EmployeeDocumentSerializer,
    ShiftSerializer,
)


# ==========================================================
# EMPLOYEE QUERYSET MIXIN
# ==========================================================

class EmployeeQuerysetMixin:
    """
    Reusable queryset logic for Employee views.

    Both EmployeeListCreateAPIView and
    EmployeeRetrieveUpdateDestroyAPIView
    call get_employee_queryset() instead of
    duplicating the same queryset logic.

    Superusers see all companies.
    Normal users see only their own company.
    """

    def get_employee_queryset(self):
        queryset = (
            Employee.objects
            .select_related(
                "company",
                "department",
                "designation",
                "reporting_manager",
                "user_account",
            )
            .filter(is_active=True)
            .order_by("employee_id")
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            company=self.request.user.company
        )


# ==========================================================
# DEPARTMENT LIST & CREATE
# ==========================================================

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

        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(
            company=self.request.user.company
        )


# ==========================================================
# DEPARTMENT DETAIL
# ==========================================================

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
        instance.save(update_fields=["is_active", "updated_at"])


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

        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(
            company=self.request.user.company
        )


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


# ==========================================================
# EMPLOYEE LIST & CREATE
# ==========================================================

class EmployeeListCreateAPIView(
    EmployeeQuerysetMixin,
    generics.ListCreateAPIView,
):
    """
    GET:
        Return all active employees.
        Filtered by company for normal users.
        Superusers see all companies.

    POST:
        Create a new employee.
        Company is injected from request.user.
    """

    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return self.get_employee_queryset()

    def get_permissions(self):

        if self.request.method == "POST":
            permission_classes = (
                IsAuthenticated,
                HasEmployeeCreatePermission,
            )
        else:
            permission_classes = (
                IsAuthenticated,
                HasEmployeeViewPermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_create(self, serializer):
        """
        Inject company from the logged-in user.
        employee_id is auto-generated in the model.
        """

        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(
                company=self.request.user.company
            )


# ==========================================================
# EMPLOYEE DETAIL
# ==========================================================

class EmployeeRetrieveUpdateDestroyAPIView(
    EmployeeQuerysetMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    GET:
        Retrieve a single employee.

    PUT/PATCH:
        Update employee details.

    DELETE:
        Soft delete — marks employee inactive.
        Does not remove from database.
        Preserves payroll and attendance history.
    """

    serializer_class = EmployeeSerializer

    def get_queryset(self):
        return self.get_employee_queryset()

    def get_permissions(self):

        if self.request.method == "GET":
            permission_classes = (
                IsAuthenticated,
                HasEmployeeViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):
            permission_classes = (
                IsAuthenticated,
                HasEmployeeUpdatePermission,
            )

        else:
            permission_classes = (
                IsAuthenticated,
                HasEmployeeDeletePermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_destroy(self, instance):
        """
        Soft delete the employee.

        Sets is_active=False and employee_status=Resigned.
        Does not delete any related data.
        Attendance, payroll and documents are preserved.
        """

        instance.is_active = False
        instance.employee_status = Employee.EmployeeStatus.RESIGNED
        instance.save(
            update_fields=[
                "is_active",
                "employee_status",
                "updated_at",
            ]
        )
        

# ==========================================================
# EMPLOYEE ADDRESS LIST & CREATE
# ==========================================================

class EmployeeAddressListCreateAPIView(
    generics.ListCreateAPIView,
):
    """
    GET:
        Return all active employee addresses.

    POST:
        Create a new employee address.
    """

    serializer_class = (
        EmployeeAddressSerializer
    )

    def get_queryset(self):

        queryset = (
            EmployeeAddress.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "address_type",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "POST":

            permission_classes = (
                IsAuthenticated,
                HasEmployeeAddressCreatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmployeeAddressViewPermission,
            )

        return [
            permission()
            for permission
            in permission_classes
        ]


# ==========================================================
# EMPLOYEE ADDRESS DETAIL
# ==========================================================

class EmployeeAddressRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    Retrieve, update and
    soft delete employee addresses.
    """

    serializer_class = (
        EmployeeAddressSerializer
    )

    def get_queryset(self):

        queryset = (
            EmployeeAddress.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "address_type",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "GET":

            permission_classes = (
                IsAuthenticated,
                HasEmployeeAddressViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):

            permission_classes = (
                IsAuthenticated,
                HasEmployeeAddressUpdatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmployeeAddressDeletePermission,
            )

        return [
            permission()
            for permission
            in permission_classes
        ]

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
                "updated_at",
            ]
        )


# ==========================================================
# EMERGENCY CONTACT LIST & CREATE
# ==========================================================

class EmergencyContactListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    GET:
        Return all active emergency contacts.

    POST:
        Create a new emergency contact.
    """

    serializer_class = (
        EmergencyContactSerializer
    )

    def get_queryset(self):

        queryset = (
            EmergencyContact.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "-is_primary",
                "contact_name",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "POST":

            permission_classes = (
                IsAuthenticated,
                HasEmergencyContactCreatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmergencyContactViewPermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]


# ==========================================================
# EMERGENCY CONTACT DETAIL
# ==========================================================

class EmergencyContactRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update and
    soft delete emergency contacts.
    """

    serializer_class = (
        EmergencyContactSerializer
    )

    def get_queryset(self):

        queryset = (
            EmergencyContact.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "-is_primary",
                "contact_name",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "GET":

            permission_classes = (
                IsAuthenticated,
                HasEmergencyContactViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):

            permission_classes = (
                IsAuthenticated,
                HasEmergencyContactUpdatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmergencyContactDeletePermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_destroy(
        self,
        instance,
    ):
        """
        Soft delete the emergency contact.
        """

        instance.is_active = False

        instance.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )


# ==========================================================
# EMPLOYEE BANK DETAIL LIST & CREATE
# ==========================================================

class EmployeeBankDetailListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    GET:
        Return all active employee bank details.

    POST:
        Create a new employee bank detail.
    """

    serializer_class = (
        EmployeeBankDetailSerializer
    )

    def get_queryset(self):

        queryset = (
            EmployeeBankDetail.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "-is_primary",
                "bank_name",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "POST":

            permission_classes = (
                IsAuthenticated,
                HasEmployeeBankDetailCreatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmployeeBankDetailViewPermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]


# ==========================================================
# EMPLOYEE BANK DETAIL DETAIL
# ==========================================================

class EmployeeBankDetailRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update and soft delete
    employee bank details.
    """

    serializer_class = (
        EmployeeBankDetailSerializer
    )

    def get_queryset(self):

        queryset = (
            EmployeeBankDetail.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "-is_primary",
                "bank_name",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "GET":

            permission_classes = (
                IsAuthenticated,
                HasEmployeeBankDetailViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):

            permission_classes = (
                IsAuthenticated,
                HasEmployeeBankDetailUpdatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmployeeBankDetailDeletePermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_destroy(
        self,
        instance,
    ):
        """
        Soft delete the bank detail.
        """

        instance.is_active = False

        instance.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

# ==========================================================
# EMPLOYEE DOCUMENT LIST & CREATE
# ==========================================================

class EmployeeDocumentListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    GET:
        Return all active employee documents.

    POST:
        Upload a new employee document.
    """

    serializer_class = (
        EmployeeDocumentSerializer
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def get_queryset(self):

        queryset = (
            EmployeeDocument.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "document_type",
                "document_name",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "POST":

            permission_classes = (
                IsAuthenticated,
                HasEmployeeDocumentCreatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmployeeDocumentViewPermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]


# ==========================================================
# EMPLOYEE DOCUMENT DETAIL
# ==========================================================

class EmployeeDocumentRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update and
    soft delete employee documents.
    """

    serializer_class = (
        EmployeeDocumentSerializer
    )

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def get_queryset(self):

        queryset = (
            EmployeeDocument.objects
            .select_related(
                "employee",
                "employee__company",
            )
            .filter(
                is_active=True,
            )
            .order_by(
                "employee",
                "document_type",
                "document_name",
            )
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            employee__company=
            self.request.user.company
        )

    def get_permissions(self):

        if self.request.method == "GET":

            permission_classes = (
                IsAuthenticated,
                HasEmployeeDocumentViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):

            permission_classes = (
                IsAuthenticated,
                HasEmployeeDocumentUpdatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasEmployeeDocumentDeletePermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_destroy(
        self,
        instance,
    ):
        """
        Soft delete employee document.
        """

        instance.is_active = False

        instance.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )


# ==========================================================
# SHIFT LIST & CREATE
# ==========================================================

class ShiftListCreateAPIView(
    generics.ListCreateAPIView
):
    """
    GET:
        Return all active shifts.

    POST:
        Create a new shift.
    """

    serializer_class = ShiftSerializer

    def get_queryset(self):

        queryset = (
            Shift.objects
            .select_related("company")
            .filter(is_active=True)
            .order_by("shift_name")
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
                HasShiftCreatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasShiftViewPermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_create(
        self,
        serializer,
    ):
        serializer.save(
            company=self.request.user.company
        )


# ==========================================================
# SHIFT DETAIL
# ==========================================================

class ShiftRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update and
    soft delete shifts.
    """

    serializer_class = ShiftSerializer

    def get_queryset(self):

        queryset = (
            Shift.objects
            .select_related("company")
            .filter(is_active=True)
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
                HasShiftViewPermission,
            )

        elif self.request.method in (
            "PUT",
            "PATCH",
        ):

            permission_classes = (
                IsAuthenticated,
                HasShiftUpdatePermission,
            )

        else:

            permission_classes = (
                IsAuthenticated,
                HasShiftDeletePermission,
            )

        return [
            permission()
            for permission in permission_classes
        ]

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
                "updated_at",
            ]
        )