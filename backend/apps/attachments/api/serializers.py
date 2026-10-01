from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.attachments.models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    """Read serializer for attachments."""

    uploaded_by = UserSerializer(read_only=True)
    is_image = serializers.BooleanField(read_only=True)
    file_extension = serializers.CharField(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = (
            "id",
            "task",
            "original_filename",
            "file_size",
            "content_type",
            "file_url",
            "file_extension",
            "is_image",
            "uploaded_by",
            "created_at",
        )
        read_only_fields = fields

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class UploadAttachmentSerializer(serializers.Serializer):
    """Write serializer for file uploads."""

    file = serializers.FileField()
