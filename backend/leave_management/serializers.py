from rest_framework import serializers

from .models import (
    LeaveType,
    LeaveBalance,
    LeaveRequest,
)


# ==========================================================
# LEAVE TYPE SERIALIZER
# ==========================================================

class LeaveTypeSerializer(
    serializers.ModelSerializer,
):
    """
    Serializer for LeaveType.

    Used for CRUD operations on leave policies.
    """

    class Meta:

        model = LeaveType

        fields = (
            "id",

            "company",

            "leave_name",

            "leave_code",

            "description",

            "max_days_per_year",

            "max_consecutive_days",

            "is_paid",

            "carry_forward",

            "requires_approval",

            "is_active",

            "created_at",

            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# ==========================================================
# LEAVE BALANCE SERIALIZER
# ==========================================================

class LeaveBalanceSerializer(
    serializers.ModelSerializer,
):
    """
    Read-only serializer for LeaveBalance.

    Leave balances are maintained by
    LeaveService.
    """

    employee_id = serializers.CharField(
        source="employee.employee_id",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    leave_type = serializers.CharField(
        source="leave_type.leave_name",
        read_only=True,
    )

    class Meta:

        model = LeaveBalance

        fields = (

            "id",

            "employee_id",

            "employee_name",

            "leave_type",

            "year",

            "allocated_days",

            "used_days",

            "remaining_days",

            "created_at",

            "updated_at",
        )

        read_only_fields = fields



# ==========================================================
# BASE LEAVE REQUEST SERIALIZER
# ==========================================================

class BaseLeaveRequestSerializer(
    serializers.ModelSerializer,
):
    """
    Base serializer for leave requests.

    Contains reusable employee and leave
    presentation fields shared across
    multiple leave serializers.
    """

    employee_id = serializers.CharField(
        source="employee.employee_id",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    department = serializers.CharField(
        source="employee.department.department_name",
        read_only=True,
        allow_null=True,
    )

    designation = serializers.CharField(
        source="employee.designation.designation_name",
        read_only=True,
        allow_null=True,
    )

    leave_type = serializers.CharField(
        source="leave_type_snapshot",
        read_only=True,
    )

    class Meta:

        model = LeaveRequest

        fields = (

            "employee_id",

            "employee_name",

            "department",

            "designation",

            "leave_type",
        )

        read_only_fields = fields


# ==========================================================
# LEAVE REQUEST CREATE SERIALIZER
# ==========================================================

class LeaveRequestCreateSerializer(
    serializers.ModelSerializer,
):
    """
    Serializer for creating a leave request.

    Only employee-provided fields are accepted.
    All business logic is handled by LeaveService.
    """

    class Meta:

        model = LeaveRequest

        fields = (

            "leave_type",

            "start_date",

            "end_date",

            "is_half_day",

            "reason",

        )

    def validate(self, attrs):
        """
        Basic validation.

        Business rules such as leave balance,
        overlap detection and holidays are
        handled by LeaveService.
        """

        if attrs["end_date"] < attrs["start_date"]:

            raise serializers.ValidationError(
                {
                    "end_date":
                    (
                        "End date cannot be "
                        "earlier than start date."
                    )
                }
            )

        return attrs
    

# ==========================================================
# LEAVE REQUEST DETAIL SERIALIZER
# ==========================================================

class LeaveRequestDetailSerializer(
    BaseLeaveRequestSerializer,
):
    """
    Read-only serializer for leave request details.
    """
    def get_approved_by(
        self,
        obj,
    ):
        """
        Return approver's full name.
        """

        if obj.approved_by is None:
            return None

        return obj.approved_by.get_full_name()

    class Meta(
        BaseLeaveRequestSerializer.Meta,
    ):

        fields = (

            "id",

            *BaseLeaveRequestSerializer.Meta.fields,

            "start_date",

            "end_date",

            "total_days",

            "is_half_day",

            "reason",

            "remarks",

            "leave_status",

            "approval_status",

            "approval_reason",

            "approved_by",

            "approved_at",

            "request_date",

            "leave_source",

            "leave_modified",

            "created_at",

            "updated_at",

        )

        read_only_fields = fields


# ==========================================================
# LEAVE APPROVAL SERIALIZER
# ==========================================================

class LeaveApprovalSerializer(
    serializers.Serializer,
):
    """
    Serializer for approving a leave request.
    """

    approval_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# LEAVE REJECT SERIALIZER
# ==========================================================

class LeaveRejectSerializer(
    serializers.Serializer,
):
    """
    Serializer for rejecting a leave request.
    """

    approval_reason = serializers.CharField()


# ==========================================================
# LEAVE CANCEL SERIALIZER
# ==========================================================

class LeaveCancelSerializer(
    serializers.Serializer,
):
    """
    Serializer for cancelling a leave request.
    """

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )


# ==========================================================
# APPROVE LEAVE SERIALIZER
# ==========================================================

class ApproveLeaveSerializer(
    serializers.Serializer,
):
    """
    Serializer for approving
    a leave request.
    """

    approval_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        default="",
    )


# ==========================================================
# REJECT LEAVE SERIALIZER
# ==========================================================

class RejectLeaveSerializer(
    serializers.Serializer,
):
    """
    Serializer for rejecting
    a leave request.
    """

    approval_reason = serializers.CharField(
        max_length=500,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )


# ==========================================================
# CANCEL LEAVE SERIALIZER
# ==========================================================

class CancelLeaveSerializer(
    serializers.Serializer,
):
    """
    Serializer for cancelling
    a leave request.
    """

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        trim_whitespace=True,
        default="",
    )