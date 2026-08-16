from rest_framework import serializers

from .models import (
    Holiday,
    Attendance,
)

from employees.models import (
    Employee,
    Shift,
)

from core.validators import (
    validate_non_empty_string,
    validate_trimmed_string,
)

class HolidaySerializer(
    serializers.ModelSerializer,
):
    """
    Serializer for the Holiday model.

    Used for:
    - Creating holidays
    - Updating holidays
    - Retrieving holiday details
    - Listing holidays
    """

    class Meta:

        model = Holiday

        fields = (
            "id",
            "company",
            "name",
            "date",
            "holiday_type",
            "description",
            "is_optional",
            "is_recurring",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

        validators = []

    # ======================================================
    # FIELD VALIDATION
    # ======================================================

    def validate_name(
        self,
        value,
    ):
        return validate_non_empty_string(
            value,
            "Holiday name",
        )

    def validate_description(
        self,
        value,
    ):
        return validate_trimmed_string(
            value,
        )

    # ======================================================
    # OBJECT VALIDATION
    # ======================================================

    def validate(
        self,
        attrs,
    ):
        """
        Validate company ownership,
        immutable company,
        and duplicate holidays.
        """

        request = self.context.get(
            "request",
        )

        company = attrs.get(
            "company",
            getattr(
                self.instance,
                "company",
                None,
            ),
        )

        holiday_date = attrs.get(
            "date",
            getattr(
                self.instance,
                "date",
                None,
            ),
        )

        # ------------------------------------------
        # Company Isolation
        # ------------------------------------------

        if (
            request
            and not request.user.is_superuser
            and company != request.user.company
        ):
            raise serializers.ValidationError(
                {
                    "company":
                    (
                        "You can only manage holidays "
                        "for your own company."
                    )
                }
            )

        # ------------------------------------------
        # Immutable Company
        # ------------------------------------------

        if (
            self.instance
            and "company" in attrs
            and attrs["company"] != self.instance.company
        ):
            raise serializers.ValidationError(
                {
                    "company":
                    (
                        "Company cannot be modified "
                        "after creation."
                    )
                }
            )

        # ------------------------------------------
        # Duplicate Holiday
        # ------------------------------------------

        queryset = Holiday.objects.filter(
            company=company,
            date=holiday_date,
        )

        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():

            raise serializers.ValidationError(
                {
                    "date":
                    (
                        "A holiday already exists "
                        "for this company on this date."
                    )
                }
            )

        return attrs
    

# ==========================================================
# ATTENDANCE SERIALIZER
# ==========================================================

class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance.

    Used for:
    - Create Attendance
    - Update Attendance
    - Retrieve Attendance
    - Attendance Reports
    """

    class Meta:

        model = Attendance

        fields = (
            "id",
            "employee",
            "shift",
            "date",
            "scheduled_start_time",
            "scheduled_end_time",
            "check_in",
            "check_out",
            "working_minutes",
            "late_minutes",
            "early_exit_minutes",
            "overtime_minutes",
            "status",
            "remarks",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "working_minutes",
            "late_minutes",
            "early_exit_minutes",
            "overtime_minutes",
            "created_at",
            "updated_at",
        )

        validators = []

    # ======================================================
    # FIELD VALIDATION
    # ======================================================

    def validate_remarks(
        self,
        value,
    ):
        return validate_trimmed_string(value)

    # ======================================================
    # OBJECT VALIDATION
    # ======================================================

    def validate(
        self,
        attrs,
    ):
        """
        Validate Attendance business rules.
        """

        employee = attrs.get(
            "employee",
            getattr(
                self.instance,
                "employee",
                None,
            ),
        )

        shift = attrs.get(
            "shift",
            getattr(
                self.instance,
                "shift",
                None,
            ),
        )

        attendance_date = attrs.get(
            "date",
            getattr(
                self.instance,
                "date",
                None,
            ),
        )

        # ------------------------------------
        # Employee Immutable
        # ------------------------------------

        if (
            self.instance
            and "employee" in attrs
            and attrs["employee"] != self.instance.employee
        ):
            raise serializers.ValidationError(
                {
                    "employee": (
                        "Employee cannot be modified "
                        "after attendance is created."
                    )
                }
            )

        # ------------------------------------
        # Shift Immutable
        # ------------------------------------

        if (
            self.instance
            and "shift" in attrs
            and attrs["shift"] != self.instance.shift
        ):
            raise serializers.ValidationError(
                {
                    "shift": (
                        "Shift cannot be modified "
                        "after attendance is created."
                    )
                }
            )

        # ------------------------------------
        # Date Immutable
        # ------------------------------------

        if (
            self.instance
            and "date" in attrs
            and attrs["date"] != self.instance.date
        ):
            raise serializers.ValidationError(
                {
                    "date": (
                        "Attendance date cannot be modified "
                        "after creation."
                    )
                }
            )

        # ------------------------------------
        # Scheduled Start Time Immutable
        # ------------------------------------

        if (
            self.instance
            and "scheduled_start_time" in attrs
            and attrs["scheduled_start_time"] != self.instance.scheduled_start_time
        ):
            raise serializers.ValidationError(
                {
                    "scheduled_start_time": (
                        "Scheduled start time cannot be modified."
                    )
                }
            )

        # ------------------------------------
        # Scheduled End Time Immutable
        # ------------------------------------

        if (
            self.instance
            and "scheduled_end_time" in attrs
            and attrs["scheduled_end_time"] != self.instance.scheduled_end_time
        ):
            raise serializers.ValidationError(
                {
                    "scheduled_end_time": (
                        "Scheduled end time cannot be modified."
                    )
                }
            )

        # ------------------------------------
        # Duplicate Attendance
        # ------------------------------------

        queryset = Attendance.objects.filter(
            employee=employee,
            date=attendance_date,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "date": (
                        "Attendance already exists "
                        "for this employee on this date."
                    )
                }
            )

        return attrs
    

# ==========================================================
# CHECK-IN SERIALIZER
# ==========================================================

class CheckInSerializer(serializers.Serializer):
    """
    Employee check-in serializer.
    """

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )

    check_in = serializers.DateTimeField()

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    def validate_remarks(
        self,
        value,
    ):
        return validate_trimmed_string(value)
    

# ==========================================================
# CHECK-OUT SERIALIZER
# ==========================================================


class CheckOutSerializer(serializers.Serializer):
    """
    Serializer for employee check-out.
    """

    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.filter(
            is_active=True,
        ),
        required=False,
        allow_null=True,
    )

    check_out = serializers.DateTimeField()

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    # ======================================================
    # FIELD VALIDATION
    # ======================================================

    def validate_remarks(
        self,
        value,
    ):
        return validate_trimmed_string(
            value,
        )