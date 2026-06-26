from rest_framework import serializers

from .models import (
    Department,
    Designation,
    Employee,
)


# ==========================================================
# DEPARTMENT SERIALIZER
# ==========================================================

class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Department model.

    Used for:
    - Creating departments
    - Updating departments
    - Retrieving department details
    - Listing departments

    Note:
    'company' is read-only. It is never accepted
    from the client. Instead it is injected
    automatically from request.user.company
    inside perform_create() in the view.
    """

    class Meta:
        model = Department

        fields = (
            "id",
            "company",
            "department_name",
            "department_code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "company",
            "created_at",
            "updated_at",
        )

    def validate_department_name(self, value):
        """
        Ensure the department name is not empty.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Department name cannot be empty."
            )

        return value

    def validate_department_code(self, value):
        """
        Ensure the department code is not empty.
        Automatically converted to uppercase.
        """

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Department code cannot be empty."
            )

        return value

    def validate(self, attrs):
        """
        Ensure department name and code
        are unique within the same company.

        Company is resolved from:
        - self.instance.company  → for updates
        - request.user.company   → for creates
        """

        request = self.context.get("request")

        if self.instance:
            company = self.instance.company
        elif request:
            company = getattr(
                request.user,
                "company",
                None,
            )

        if company is None:
            return attrs
        

        department_name = attrs.get(
            "department_name",
            getattr(self.instance, "department_name", None),
        )

        department_code = attrs.get(
            "department_code",
            getattr(self.instance, "department_code", None),
        )

        queryset = Department.objects.filter(
            company=company
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.filter(
            department_name=department_name
        ).exists():
            raise serializers.ValidationError(
                {
                    "department_name":
                    "Department name already exists "
                    "for this company."
                }
            )

        if queryset.filter(
            department_code=department_code
        ).exists():
            raise serializers.ValidationError(
                {
                    "department_code":
                    "Department code already exists "
                    "for this company."
                }
            )

        return attrs


# ==========================================================
# DESIGNATION SERIALIZER
# ==========================================================

class DesignationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Designation model.

    Used for:
    - Creating designations
    - Updating designations
    - Retrieving designation details
    - Listing designations

    Note:
    'company' is read-only. It is never accepted
    from the client. Instead it is injected
    automatically from request.user.company
    inside perform_create() in the view.
    """

    class Meta:
        model = Designation

        fields = (
            "id",
            "company",
            "designation_name",
            "designation_code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "company",
            "created_at",
            "updated_at",
        )

    def validate_designation_name(self, value):
        """
        Ensure the designation name is not empty.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Designation name cannot be empty."
            )

        return value

    def validate_designation_code(self, value):
        """
        Ensure the designation code is not empty.
        Automatically converted to uppercase.
        """

        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Designation code cannot be empty."
            )

        return value

    def validate(self, attrs):
        """
        Ensure designation name and code
        are unique within the same company.

        Company is resolved from:
        - self.instance.company  → for updates
        - request.user.company   → for creates
        """

        request = self.context.get("request")

        if self.instance:
            company = self.instance.company
        elif request:
            company = getattr(
            request.user,
            "company",
            None,
        )

        if company is None:
            return attrs
        

        designation_name = attrs.get(
            "designation_name",
            getattr(self.instance, "designation_name", None),
        )

        designation_code = attrs.get(
            "designation_code",
            getattr(self.instance, "designation_code", None),
        )

        queryset = Designation.objects.filter(
            company=company
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.filter(
            designation_name=designation_name
        ).exists():
            raise serializers.ValidationError(
                {
                    "designation_name":
                    "Designation name already exists "
                    "for this company."
                }
            )

        if queryset.filter(
            designation_code=designation_code
        ).exists():
            raise serializers.ValidationError(
                {
                    "designation_code":
                    "Designation code already exists "
                    "for this company."
                }
            )

        return attrs


# ==========================================================
# EMPLOYEE SERIALIZER
# ==========================================================

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Employee model.

    Read-only nested fields return names
    alongside IDs so the frontend does not
    need extra API calls to display them.

    Write operations accept only IDs for
    FK fields (department, designation,
    reporting_manager, user_account).

    company is injected from request.user.company
    in perform_create() — never trusted from client.
    """

    # ──────────────────────────────────────
    # READ ONLY NESTED FIELDS
    # ──────────────────────────────────────

    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="department.department_name",
        read_only=True,
        allow_null=True,
        default=None,
    )

    designation_name = serializers.CharField(
        source="designation.designation_name",
        read_only=True,
        allow_null=True,
        default=None,
    )

    reporting_manager_name = serializers.SerializerMethodField()

    full_name = serializers.CharField(
        read_only=True,
    )

    # ──────────────────────────────────────
    # META
    # ──────────────────────────────────────

    class Meta:
        model = Employee

        fields = (
            # Identification
            "id",
            "employee_id",
            "full_name",

            # Personal
            "first_name",
            "middle_name",
            "last_name",
            "gender",
            "date_of_birth",
            "marital_status",
            "blood_group",
            "profile_photo",

            # Contact
            "email",
            "phone",
            "alternate_phone",

            # Organization
            "company",
            "company_name",
            "department",
            "department_name",
            "designation",
            "designation_name",
            "reporting_manager",
            "reporting_manager_name",
            "user_account",
            "employment_type",
            "joining_date",
            "confirmation_date",

            # Salary
            "basic_salary",

            # Status
            "employee_status",
            "is_active",
            "resignation_date",
            "termination_date",
            "retirement_date",

            # Audit
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "employee_id",
            "full_name",
            "company_name",
            "department_name",
            "designation_name",
            "reporting_manager_name",
            "created_at",
            "updated_at",
        )

    # ──────────────────────────────────────
    # METHOD FIELDS
    # ──────────────────────────────────────

    def get_reporting_manager_name(self, obj):
        """
        Returns the full name of the reporting
        manager if one is assigned.
        Returns None if no manager is assigned.
        """

        if obj.reporting_manager:
            return obj.reporting_manager.full_name

        return None

    # ──────────────────────────────────────
    # FIELD VALIDATION
    # ──────────────────────────────────────

    def validate_first_name(self, value):

        """
        Ensure first name is not empty.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name cannot be empty."
            )

        return value.title()

    def validate_last_name(self, value):
        """
        Ensure last name is not empty.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name cannot be empty."
            )

        return value.title()

    def validate_email(self, value):
        """
        Normalize email to lowercase.
        """

        return value.strip().lower()
    

    def validate_company(self, value):
        """
        Allow only superusers to choose
        the company manually.

        Normal users can create employees
        only in their own company.
        """

        request = self.context.get("request")

        if not request:
            return value

        if request.user.is_superuser:
            return value

        if value != request.user.company:
            raise serializers.ValidationError(
                "You cannot assign another company."
            )

        return value
    
    def validate_phone(self, value):
        """
        Remove extra spaces from phone number.
        """

        return value.strip()
    
    def validate_alternate_phone(self, value):
        """
        Remove extra spaces from alternate phone.
        """

        return value.strip()

    def validate_basic_salary(self, value):
        """
        Ensure salary is not negative.
        """

        if value < 0:
            raise serializers.ValidationError(
                "Salary cannot be negative."
            )

        return value

    # ──────────────────────────────────────
    # CROSS FIELD VALIDATION
    # ──────────────────────────────────────

    def validate(self, attrs):
        """
        Cross-field validation.

        Validates:
        - Email uniqueness per company
        - Department belongs to same company
        - Designation belongs to same company
        - Reporting manager belongs to same company
        - Employee is not their own manager
        - Confirmation date is after joining date
        - Resignation date required when status Resigned
        - Termination date required when status Terminated
        - Retirement date required when status Retired
        """

        request = self.context.get("request")

        # Resolve company
        if self.instance:
            company = self.instance.company

        elif request and request.user.is_superuser:
            company = attrs.get("company")

        else:
            company = getattr(
                request.user,
                "company",
                None,
            )

        if company is None:
            return attrs
        

        email = attrs.get(
            "email",
            getattr(self.instance, "email", None),
        )

        department = attrs.get(
            "department",
            getattr(self.instance, "department", None),
        )

        designation = attrs.get(
            "designation",
            getattr(self.instance, "designation", None),
        )

        reporting_manager = attrs.get(
            "reporting_manager",
            getattr(self.instance, "reporting_manager", None),
        )

        joining_date = attrs.get(
            "joining_date",
            getattr(self.instance, "joining_date", None),
        )

        confirmation_date = attrs.get(
            "confirmation_date",
            getattr(self.instance, "confirmation_date", None),
        )

        employee_status = attrs.get(
            "employee_status",
            getattr(self.instance, "employee_status", None),
        )

        resignation_date = attrs.get(
            "resignation_date",
            getattr(self.instance, "resignation_date", None),
        )

        termination_date = attrs.get(
            "termination_date",
            getattr(self.instance, "termination_date", None),
        )

        retirement_date = attrs.get(
            "retirement_date",
            getattr(self.instance, "retirement_date", None),
        )

        # Email uniqueness per company
        email_qs = Employee.objects.filter(
            company=company,
            email=email,
        )

        if self.instance:
            email_qs = email_qs.exclude(pk=self.instance.pk)

        if email_qs.exists():
            raise serializers.ValidationError(
                {
                    "email":
                    "An employee with this email "
                    "already exists in this company."
                }
            )

        # Department must belong to same company
        if department and department.company != company:
            raise serializers.ValidationError(
                {
                    "department":
                    "Department does not belong "
                    "to this company."
                }
            )

        # Designation must belong to same company
        if designation and designation.company != company:
            raise serializers.ValidationError(
                {
                    "designation":
                    "Designation does not belong "
                    "to this company."
                }
            )

        # Reporting manager must belong to same company
        if reporting_manager and reporting_manager.company != company:
            raise serializers.ValidationError(
                {
                    "reporting_manager":
                    "Reporting manager does not "
                    "belong to this company."
                }
            )

        # Employee cannot be their own manager
        if (
            reporting_manager
            and self.instance
            and reporting_manager.pk == self.instance.pk
        ):
            raise serializers.ValidationError(
                {
                    "reporting_manager":
                    "An employee cannot be "
                    "their own reporting manager."
                }
            )

        # Confirmation date must be after joining date
        if confirmation_date and joining_date:
            if confirmation_date < joining_date:
                raise serializers.ValidationError(
                    {
                        "confirmation_date":
                        "Confirmation date cannot be "
                        "before joining date."
                    }
                )

        # Resignation date required when Resigned
        if (
            employee_status == Employee.EmployeeStatus.RESIGNED
            and not resignation_date
        ):
            raise serializers.ValidationError(
                {
                    "resignation_date":
                    "Resignation date is required "
                    "when status is Resigned."
                }
            )

        # Termination date required when Terminated
        if (
            employee_status == Employee.EmployeeStatus.TERMINATED
            and not termination_date
        ):
            raise serializers.ValidationError(
                {
                    "termination_date":
                    "Termination date is required "
                    "when status is Terminated."
                }
            )

        # Retirement date required when Retired
        if (
            employee_status == Employee.EmployeeStatus.RETIRED
            and not retirement_date
        ):
            raise serializers.ValidationError(
                {
                    "retirement_date":
                    "Retirement date is required "
                    "when status is Retired."
                }
            )

        return attrs