from django.urls import path
from .views import (
    NotificationListAPIView,
    UnreadNotificationCountAPIView,
    MarkNotificationReadAPIView,
    MarkAllNotificationsReadAPIView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path("unread-count/", UnreadNotificationCountAPIView.as_view(), name="unread-count"),
    path("<int:pk>/read/", MarkNotificationReadAPIView.as_view(), name="mark-read"),
    path("mark-all-read/", MarkAllNotificationsReadAPIView.as_view(), name="mark-all-read"),
]
