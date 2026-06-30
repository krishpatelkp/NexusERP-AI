from rest_framework import serializers

from .models import Payment


# ==========================================================
# PAYMENT SERIALIZER
# ==========================================================

class PaymentSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    employee_code = serializers.CharField(
        source="employee.employee_id",
        read_only=True,
    )

    payslip_number = serializers.CharField(
        source="payslip.payslip_number",
        read_only=True,
    )

    processed_by_name = serializers.SerializerMethodField()

    class Meta:

        model = Payment

        fields = (
            "id",
            "company",
            "company_name",
            "payslip",
            "payslip_number",
            "employee",
            "employee_code",
            "employee_name",
            "payment_number",
            "amount",
            "payment_method",
            "status",
            "payment_date",
            "transaction_id",
            "bank_reference_number",
            "failure_reason",
            "remarks",
            "processed_by",
            "processed_by_name",
            "processed_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "company_name",
            "employee_name",
            "employee_code",
            "payslip_number",
            "payment_number",
            "processed_by_name",
            "processed_at",
            "created_at",
            "updated_at",
        )

    def get_processed_by_name(self, obj):

        if obj.processed_by:
            return obj.processed_by.username

        return None
    

# ==========================================================
# CREATE PAYMENT SERIALIZER
# ==========================================================

class CreatePaymentSerializer(serializers.Serializer):

    payslip = serializers.IntegerField()

    payment_method = serializers.CharField(
        max_length=50,
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
    )



# ==========================================================
# MARK PROCESSING SERIALIZER
# ==========================================================

class MarkProcessingSerializer(serializers.Serializer):

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
    )


# ==========================================================
# MARK PAID SERIALIZER
# ==========================================================

class MarkPaidSerializer(serializers.Serializer):

    payment_date = serializers.DateField()

    payment_method = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
    )

    transaction_id = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    bank_reference_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
    )


# ==========================================================
# MARK FAILED SERIALIZER
# ==========================================================

class MarkFailedSerializer(serializers.Serializer):

    failure_reason = serializers.CharField()

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
    )


# ==========================================================
# CANCEL PAYMENT SERIALIZER
# ==========================================================

class CancelPaymentSerializer(serializers.Serializer):

    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
    )