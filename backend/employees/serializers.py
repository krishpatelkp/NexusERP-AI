from rest_framework import serializers

from .models import (
    Department,
    Designation,
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
        elif request and request.user.company:
            company = request.user.company
        else:
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
        elif request and request.user.company:
            company = request.user.company
        else:
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