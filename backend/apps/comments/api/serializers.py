from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.comments.models import Comment


class CommentReplySerializer(serializers.ModelSerializer):
    """Read serializer for nested replies (one level deep)."""

    author = UserSerializer(read_only=True)
    mentions = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "body",
            "is_edited",
            "mentions",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    """Read serializer for top-level comments with nested replies."""

    author = UserSerializer(read_only=True)
    mentions = UserSerializer(many=True, read_only=True)
    replies = CommentReplySerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "task",
            "author",
            "body",
            "parent",
            "is_edited",
            "mentions",
            "replies",
            "reply_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_reply_count(self, obj):
        return obj.replies.count()


class CreateCommentSerializer(serializers.Serializer):
    body = serializers.CharField()
    parent_id = serializers.UUIDField(required=False, allow_null=True)


class UpdateCommentSerializer(serializers.Serializer):
    body = serializers.CharField()
