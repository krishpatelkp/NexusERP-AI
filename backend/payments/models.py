from django.core.exceptions import ValidationError
from django.db import models

from company.models import Company


# ==========================================================
# PAYMENT STATUS
# ==========================================================

class PaymentStatus(models.TextChoices):
    """
    Lifecycle of a salary payment.

    Pending     → Payment created, not yet sent to bank/processor
    Processing  → Payment has been submitted for processing
    Paid        → Payment confirmed successful
    Failed      → Payment attempt failed
    Cancelled   → Payment was cancelled before completion

    Lifecycle:

        Pending
           ↓
        Processing
           ↓
        Paid  ──or──  Failed
           ↓
        (Failed can be retried → back to Pending)

        Cancelled can happen from Pending or Processing only.
        Paid is a terminal state and can never change.
    """

    PENDING    = "Pending",    "Pending"
    PROCESSING = "Processing", "Processing"
    PAID       = "Paid",       "Paid"
    FAILED     = "Failed",     "Failed"
    CANCELLED  = "Cancelled",  "Cancelled"


# ==========================================================
# PAYMENT METHOD
# ==========================================================

class PaymentMethod(models.TextChoices):
    """
    How the payment was/will be disbursed.
    """

    BANK_TRANSFER = "Bank Transfer", "Bank Transfer"
    UPI           = "UPI",           "UPI"
    CASH          = "Cash",          "Cash"
    CHEQUE        = "Cheque",        "Cheque"
    NEFT          = "NEFT",          "NEFT"
    RTGS          = "RTGS",          "RTGS"
    IMPS          = "IMPS",          "IMPS"


# ==========================================================
# PAYMENT
# ==========================================================

class Payment(models.Model):
    """
    Represents a single salary payment made against
    one Payslip.

    Design
    ------
    Payment information is intentionally kept OUT of
    the Payslip model. A payslip describes what an
    employee is OWED; a Payment describes the actual
    money movement that settles that debt.

    This separation means:
        - A payslip can exist before payment happens
          (Payslip.status = Issued, no Payment yet)
        - A failed payment can be retried by creating
          a new payment attempt without touching the
          payslip at all
        - Payment history and salary calculation
          history evolve independently

    Relationship
    ------------
        Company
           ↓
        Payroll Run
           ↓
        Payslip
           ↓
        Payment   (one-to-one)

    Each payslip has at most ONE active (non-cancelled,
    non-failed) payment at a time. Failed/cancelled
    payments are kept as permanent history, and a new
    Payment row is created for the retry — payments
    are never edited into a different attempt.

    Snapshot Fields
    ---------------
    employee and payslip are both stored, but employee
    details that could change later (name) are NOT
    snapshotted here because Payslip already owns that
    snapshot. Payment only snapshots the amount, which
    is the figure actually authorized for transfer and
    must never silently change even if the payslip is
    later recalculated by a new payroll run.

    Immutability
    ------------
    Once status = Paid, a Payment record becomes
    immutable. No fields may be changed. This is
    enforced in the service layer, not the model,
    because the model layer doesn't have enough
    context to distinguish "creating a Paid record
    during a migration/import" from "editing an
    existing Paid record".
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    payslip = models.ForeignKey(
        "payroll.Payslip",
        on_delete=models.PROTECT,
        related_name="payment",
        help_text=(
            "Cannot delete a payslip that "
            "has a payment record."
        ),
    )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="payments",
        help_text=(
            "Cannot delete an employee that "
            "has payment history."
        ),
    )

    # ──────────────────────────────────────
    # IDENTIFICATION
    # ──────────────────────────────────────

    payment_number = models.CharField(
        max_length=30,
        unique=True,
        help_text=(
            "Internal unique payment reference. "
            "e.g. PAY-2026-000001"
        ),
    )

    # ──────────────────────────────────────
    # PAYMENT DETAILS
    # ──────────────────────────────────────

    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Date the payment was actually "
            "processed/sent. Left blank while Pending."
        ),
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=(
            "Amount authorized for this payment. "
            "Snapshot — independent of later payslip "
            "recalculations."
        ),
    )

    # ──────────────────────────────────────
    # BANK / TRANSACTION REFERENCES
    # ──────────────────────────────────────

    bank_reference_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=(
            "Bank-issued reference number for this "
            "transfer, if applicable."
        ),
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=(
            "Payment gateway / processor transaction ID "
            "(e.g. Razorpay payout ID)."
        ),
    )

    failure_reason = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Populated when status = Failed. "
            "Explains why the payment did not go through."
        ),
    )

    # ──────────────────────────────────────
    # AUDIT
    # ──────────────────────────────────────

    remarks = models.TextField(
        blank=True,
        default="",
    )

    processed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_processed",
        help_text=(
            "User who last moved this payment "
            "through the workflow."
        ),
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

        verbose_name = "Payment"

        verbose_name_plural = "Payments"

        constraints = [

            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="payment_amount_positive",
            ),

        ]

        indexes = [

            models.Index(
                fields=["company"],
            ),

            models.Index(
                fields=["employee"],
            ),

            models.Index(
                fields=["status"],
            ),

            models.Index(
                fields=["payment_method"],
            ),

            models.Index(
                fields=["payment_number"],
            ),

            models.Index(
                fields=["transaction_id"],
            ),

        ]

    # ======================================================
    # VALIDATION
    # ======================================================

    def clean(self):

        super().clean()

        if self.payment_number is not None:
            self.payment_number = (
                self.payment_number.strip().upper()
            )

        if self.bank_reference_number is not None:
            self.bank_reference_number = (
                self.bank_reference_number.strip()
            )

        if self.transaction_id is not None:
            self.transaction_id = (
                self.transaction_id.strip()
            )

        if self.failure_reason is not None:
            self.failure_reason = (
                self.failure_reason.strip()
            )

        if self.remarks is not None:
            self.remarks = self.remarks.strip()

        if not self.payment_number:
            raise ValidationError(
                {
                    "payment_number":
                    "Payment number is required."
                }
            )

        if self.amount is not None and self.amount <= 0:
            raise ValidationError(
                {
                    "amount":
                    "Payment amount must be greater than zero."
                }
            )

        # Payslip must belong to same company
        if (
            self.payslip
            and self.company
            and self.payslip.company != self.company
        ):
            raise ValidationError(
                {
                    "payslip":
                    (
                        "Payslip does not belong "
                        "to this company."
                    )
                }
            )

        # Employee must belong to same company
        if (
            self.employee
            and self.company
            and self.employee.company != self.company
        ):
            raise ValidationError(
                {
                    "employee":
                    (
                        "Employee does not belong "
                        "to this company."
                    )
                }
            )

        # Employee on the payment must match
        # the employee on the payslip
        if (
            self.payslip
            and self.employee
            and self.payslip.employee != self.employee
        ):
            raise ValidationError(
                {
                    "employee":
                    (
                        "Employee does not match "
                        "the employee on the payslip."
                    )
                }
            )

        # Status-dependent field requirements
        if (
            self.status == PaymentStatus.FAILED
            and not self.failure_reason
        ):
            raise ValidationError(
                {
                    "failure_reason":
                    (
                        "Failure reason is required "
                        "when status is Failed."
                    )
                }
            )

        if (
            self.status == PaymentStatus.PAID
            and not self.payment_date
        ):
            raise ValidationError(
                {
                    "payment_date":
                    (
                        "Payment date is required "
                        "when status is Paid."
                    )
                }
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(self, *args, **kwargs):

        if self.payment_number:
            self.payment_number = (
                self.payment_number.strip().upper()
            )

        if self.bank_reference_number:
            self.bank_reference_number = (
                self.bank_reference_number.strip()
            )

        if self.transaction_id:
            self.transaction_id = (
                self.transaction_id.strip()
            )

        if self.failure_reason:
            self.failure_reason = (
                self.failure_reason.strip()
            )

        if self.remarks:
            self.remarks = self.remarks.strip()

        self.full_clean()

        super().save(*args, **kwargs)

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def is_terminal(self):
        """
        Returns True if this payment is in a final
        state that the service layer should treat
        as immutable (Paid) or closed (Cancelled).
        """
        return self.status in (
            PaymentStatus.PAID,
            PaymentStatus.CANCELLED,
        )

    @property
    def is_retryable(self):
        """
        Returns True if a Failed payment is eligible
        to be retried (moved back to Pending).
        """
        return self.status == PaymentStatus.FAILED

    # ======================================================
    # STR
    # ======================================================

    def __str__(self):

        return (
            f"{self.payment_number}"
            f" — "
            f"{self.employee.employee_id}"
            f" ₹{self.amount}"
            f" ({self.status})"
        )