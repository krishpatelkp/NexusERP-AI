from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """

    sender_email = serializers.EmailField(
        source="sender.email",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Notification
        fields = (
            "id",
            "company",
            "recipient",
            "sender",
            "sender_email",
            "notification_type",
            "title",
            "message",
            "link",
            "is_read",
            "read_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "company",
            "recipient",
            "sender",
            "created_at",
        )


class UnreadCountSerializer(serializers.Serializer):
    """
    Serializer for unread notifications count.
    """

    unread_count = serializers.IntegerField()
