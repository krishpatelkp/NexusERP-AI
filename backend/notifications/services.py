from django.utils import timezone
from .models import Notification, NotificationType


class NotificationService:
    """
    Service layer for managing notifications.
    Ensures company isolation and provides helper methods to create and update notifications.
    """

    def __init__(self, company):
        self.company = company

    def send_notification(
        self,
        recipient,
        title: str,
        message: str,
        notification_type: str = NotificationType.SYSTEM,
        sender=None,
        link: str = "",
    ) -> Notification:
        """
        Create and send a notification to a specific user.
        """
        return Notification.objects.create(
            company=self.company,
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )

    def get_user_notifications(self, user, unread_only: bool = False):
        """
        Get all notifications for a specific user within the company.
        """
        qs = Notification.objects.filter(
            company=self.company,
            recipient=user,
        )
        if unread_only:
            qs = qs.filter(is_read=False)
        return qs

    def get_unread_count(self, user) -> int:
        """
        Return the count of unread notifications for a user.
        """
        return Notification.objects.filter(
            company=self.company,
            recipient=user,
            is_read=False,
        ).count()

    def mark_as_read(self, notification_id: int, user) -> Notification:
        """
        Mark a single notification as read.
        """
        notification = Notification.objects.get(
            id=notification_id,
            company=self.company,
            recipient=user,
        )
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
        return notification

    def mark_all_as_read(self, user) -> int:
        """
        Mark all notifications as read for a user.
        """
        updated_count = Notification.objects.filter(
            company=self.company,
            recipient=user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )
        return updated_count
