from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import NotificationSerializer, UnreadCountSerializer
from .services import NotificationService


class NotificationListAPIView(APIView):
    """
    GET /api/notifications/
    List notifications for the logged-in user.
    Query param: ?unread_only=true
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread_only = request.query_params.get("unread_only", "").lower() in ("true", "1")
        company = getattr(request.user, "company", None)
        if not company and hasattr(request.user, "employee_profile"):
            company = request.user.employee_profile.company

        if not company:
            return Response({"detail": "User has no company associated."}, status=status.HTTP_400_BAD_REQUEST)

        service = NotificationService(company=company)
        notifications = service.get_user_notifications(user=request.user, unread_only=unread_only)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnreadNotificationCountAPIView(APIView):
    """
    GET /api/notifications/unread-count/
    Return count of unread notifications for badge counters.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        company = getattr(request.user, "company", None)
        if not company and hasattr(request.user, "employee_profile"):
            company = request.user.employee_profile.company

        if not company:
            return Response({"detail": "User has no company associated."}, status=status.HTTP_400_BAD_REQUEST)

        service = NotificationService(company=company)
        count = service.get_unread_count(user=request.user)
        return Response({"unread_count": count}, status=status.HTTP_200_OK)


class MarkNotificationReadAPIView(APIView):
    """
    PATCH /api/notifications/<int:pk>/read/
    Mark a single notification as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        company = getattr(request.user, "company", None)
        if not company and hasattr(request.user, "employee_profile"):
            company = request.user.employee_profile.company

        if not company:
            return Response({"detail": "User has no company associated."}, status=status.HTTP_400_BAD_REQUEST)

        service = NotificationService(company=company)
        try:
            notification = service.mark_as_read(notification_id=pk, user=request.user)
        except Exception:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkAllNotificationsReadAPIView(APIView):
    """
    POST /api/notifications/mark-all-read/
    Mark all notifications as read for the logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company = getattr(request.user, "company", None)
        if not company and hasattr(request.user, "employee_profile"):
            company = request.user.employee_profile.company

        if not company:
            return Response({"detail": "User has no company associated."}, status=status.HTTP_400_BAD_REQUEST)

        service = NotificationService(company=company)
        updated_count = service.mark_all_as_read(user=request.user)
        return Response({
            "message": f"Successfully marked {updated_count} notifications as read.",
            "updated_count": updated_count
        }, status=status.HTTP_200_OK)
