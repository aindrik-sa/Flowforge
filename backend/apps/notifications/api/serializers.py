from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Read-only serializer for notifications."""

    recipient = UserSerializer(read_only=True)
    actor = UserSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "recipient",
            "actor",
            "verb",
            "target_type",
            "target_id",
            "is_read",
            "created_at",
        )
        read_only_fields = fields

    def get_target_type(self, obj):
        if obj.target_content_type:
            return obj.target_content_type.model
        return None

    def get_target_id(self, obj):
        return obj.target_object_id
