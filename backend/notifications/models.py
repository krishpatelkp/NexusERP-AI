from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    SYSTEM = "SYSTEM", "System"
    LEAVE_REQUEST = "LEAVE_REQUEST", "Leave Request"
    LEAVE_APPROVAL = "LEAVE_APPROVAL", "Leave Approval"
    LEAVE_REJECTION = "LEAVE_REJECTION", "Leave Rejection"
    PAYROLL_PROCESSED = "PAYROLL_PROCESSED", "Payroll Processed"
    PAYMENT_PENDING = "PAYMENT_PENDING", "Payment Pending"
    ASSET_ASSIGNED = "ASSET_ASSIGNED", "Asset Assigned"
    MAINTENANCE_DUE = "MAINTENANCE_DUE", "Maintenance Due"
    ATTENDANCE_EXCEPTION = "ATTENDANCE_EXCEPTION", "Attendance Exception"


class Notification(models.Model):
    """
    In-app Notification model with multi-tenant company isolation.
    """

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications_received",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_sent",
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    link = models.CharField(
        max_length=500,
        blank=True,
        default="",
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["company", "recipient"]),
        ]

    def __str__(self):
        return f"{self.recipient.email} — {self.title} ({'Read' if self.is_read else 'Unread'})"
