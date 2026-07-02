from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import (
    Payment,
    PaymentStatus,
)


# ==========================================================
# PAYMENT SERVICE
# ==========================================================

class PaymentService:
    """
    Business logic for the Payments module.

    Responsibilities
    ----------------
    - Create Payment
    - Mark Processing
    - Mark Paid
    - Mark Failed
    - Cancel Payment
    """

    def __init__(
        self,
        *,
        company,
    ):
        self.company = company


    # ======================================================
    # CREATE PAYMENT
    # ======================================================

    @transaction.atomic
    def create_payment(
        self,
        *,
        payslip,
        payment_method,
        processed_by=None,
        remarks="",
    ):
        """
        Create a new payment for a payslip.
        """

        # ------------------------------------------
        # Validate Payslip
        # ------------------------------------------

        if payslip is None:
            raise ValidationError(
                "Payslip is required."
            )

        if payslip.company != self.company:
            raise ValidationError(
                (
                    "Payslip does not belong "
                    "to this company."
                )
            )

        employee = payslip.employee

        if employee.company != self.company:
            raise ValidationError(
                (
                    "Employee does not belong "
                    "to this company."
                )
            )

        # ------------------------------------------
        # Check Existing Active Payment
        # ------------------------------------------

        existing_payment = (
            Payment.objects.filter(
                payslip=payslip,
                status__in=[
                    PaymentStatus.PENDING,
                    PaymentStatus.PROCESSING,
                    PaymentStatus.PAID,
                ],
            )
            .exists()
        )

        if existing_payment:
            raise ValidationError(
                (
                    "An active payment already "
                    "exists for this payslip."
                )
            )

        # ------------------------------------------
        # Generate Payment Number
        # ------------------------------------------

        year = timezone.now().year

        last = (
        Payment.objects
        .filter(company=self.company)
        .order_by("-id")
        .values_list("payment_number", flat=True)
        .first()
        )

        if last:
            try:
                last_number = int(last.split("-")[-1])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0

        payment_number = f"PAY-{year}-{last_number + 1:06d}"

        # ------------------------------------------
        # Create Payment
        # ------------------------------------------

        payment = Payment.objects.create(
            company=self.company,
            payslip=payslip,
            employee=employee,
            payment_number=payment_number,
            payment_method=payment_method,
            status=PaymentStatus.PENDING,
            amount=payslip.net_salary,
            processed_by=processed_by,
            remarks=remarks,
        )

        return payment
    

    # ======================================================
    # MARK PAYMENT AS PROCESSING
    # ======================================================

    @transaction.atomic
    def mark_processing(
        self,
        *,
        payment,
        processed_by=None,
    ):
        """
        Mark a payment as Processing.

        Business Rules
        --------------
        - Payment must belong to this company.
        - Only Pending payments can be processed.
        """

        # ------------------------------------------
        # Validate Payment
        # ------------------------------------------

        if payment.company != self.company:
            raise ValidationError(
                (
                    "Payment does not belong "
                    "to this company."
                )
            )

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError(
                (
                    "Only Pending payments can "
                    "be marked as Processing."
                )
            )

        # ------------------------------------------
        # Update Payment
        # ------------------------------------------

        payment.status = PaymentStatus.PROCESSING
        payment.processed_by = processed_by
        payment.processed_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "processed_by",
                "processed_at",
                "updated_at",
            ]
        )

        return payment
    

        # ======================================================
    # MARK PAYMENT AS PAID
    # ======================================================

    @transaction.atomic
    def mark_paid(
        self,
        *,
        payment,
        payment_date,
        payment_method=None,
        transaction_id="",
        bank_reference_number="",
        processed_by=None,
        remarks="",
    ):
        """
        Mark a payment as Paid.

        Business Rules
        --------------
        - Payment must belong to this company.
        - Only Processing payments can become Paid.
        - Payment date is required.
        """

        # ------------------------------------------
        # Validate Payment
        # ------------------------------------------

        if payment.company != self.company:
            raise ValidationError(
                (
                    "Payment does not belong "
                    "to this company."
                )
            )

        if payment.status != PaymentStatus.PROCESSING:
            raise ValidationError(
                (
                    "Only Processing payments "
                    "can be marked as Paid."
                )
            )

        if payment_date is None:
            raise ValidationError(
                "Payment date is required."
            )

        # ------------------------------------------
        # Update Payment
        # ------------------------------------------

        payment.status = PaymentStatus.PAID
        payment.payment_date = payment_date

        if payment_method:
            payment.payment_method = payment_method

        if transaction_id:
            payment.transaction_id = transaction_id.strip()

        if bank_reference_number:
            payment.bank_reference_number = (
                bank_reference_number.strip()
            )

        if remarks:
            payment.remarks = remarks.strip()

        payment.processed_by = processed_by
        payment.processed_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "payment_date",
                "payment_method",
                "transaction_id",
                "bank_reference_number",
                "remarks",
                "processed_by",
                "processed_at",
                "updated_at",
            ]
        )

        return payment
    


        # ======================================================
    # MARK PAYMENT AS FAILED
    # ======================================================

    @transaction.atomic
    def mark_failed(
        self,
        *,
        payment,
        failure_reason,
        processed_by=None,
        remarks="",
    ):
        """
        Mark a payment as Failed.

        Business Rules
        --------------
        - Payment must belong to this company.
        - Only Processing payments can become Failed.
        - Failure reason is required.
        """

        if payment.company != self.company:
            raise ValidationError(
                "Payment does not belong to this company."
            )

        if payment.status != PaymentStatus.PROCESSING:
            raise ValidationError(
                (
                    "Only Processing payments "
                    "can be marked as Failed."
                )
            )

        if not failure_reason.strip():
            raise ValidationError(
                "Failure reason is required."
            )

        payment.status = PaymentStatus.FAILED
        payment.failure_reason = failure_reason.strip()

        if remarks:
            payment.remarks = remarks.strip()

        payment.processed_by = processed_by
        payment.processed_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "failure_reason",
                "remarks",
                "processed_by",
                "processed_at",
                "updated_at",
            ]
        )

        return payment
    

        # ======================================================
    # CANCEL PAYMENT
    # ======================================================

    @transaction.atomic
    def cancel_payment(
        self,
        *,
        payment,
        processed_by=None,
        remarks="",
    ):
        """
        Cancel a payment.

        Business Rules
        --------------
        - Payment must belong to this company.
        - Paid payments cannot be cancelled.
        """

        if payment.company != self.company:
            raise ValidationError(
                "Payment does not belong to this company."
            )

        if payment.status == PaymentStatus.PAID:
            raise ValidationError(
                "Paid payments cannot be cancelled."
            )

        if payment.status == PaymentStatus.CANCELLED:
            raise ValidationError(
                "Payment is already cancelled."
            )

        payment.status = PaymentStatus.CANCELLED

        if remarks:
            payment.remarks = remarks.strip()

        payment.processed_by = processed_by
        payment.processed_at = timezone.now()

        payment.save(
            update_fields=[
                "status",
                "remarks",
                "processed_by",
                "processed_at",
                "updated_at",
            ]
        )

        return payment
    
