from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.projects.models import Workspace, Project, ProjectMember, Board, BoardColumn

User = get_user_model()


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = (
            "id",
            "organization",
            "name",
            "slug",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateWorkspaceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, default="", allow_blank=True)


class UpdateWorkspaceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "workspace",
            "name",
            "key",
            "slug",
            "description",
            "status",
            "start_date",
            "due_date",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateProjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    key = serializers.CharField(max_length=10)
    slug = serializers.SlugField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    status = serializers.ChoiceField(
        choices=Project.Status.choices,
        default=Project.Status.PLANNED,
    )
    start_date = serializers.DateField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)


class UpdateProjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Project.Status.choices, required=False)
    start_date = serializers.DateField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)


class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = (
            "id",
            "user",
            "role",
            "joined_at",
        )
        read_only_fields = fields


class AddProjectMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=ProjectMember.Role.choices,
        default=ProjectMember.Role.MEMBER,
    )

    def validate_email(self, value: str) -> str:
        email = value.lower().strip()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return email


class ChangeProjectMemberRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=ProjectMember.Role.choices)


# ---------------------------------------------------------------------------
# Board Serializers
# ---------------------------------------------------------------------------


class BoardColumnSerializer(serializers.ModelSerializer):
    """Read serializer for board columns."""

    class Meta:
        model = BoardColumn
        fields = (
            "id",
            "name",
            "slug",
            "position",
            "color",
            "wip_limit",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class BoardSerializer(serializers.ModelSerializer):
    """Read serializer for boards, includes nested columns."""

    columns = BoardColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = (
            "id",
            "project",
            "name",
            "slug",
            "description",
            "is_default",
            "columns",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateBoardSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    is_default = serializers.BooleanField(default=False)


class UpdateBoardSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_default = serializers.BooleanField(required=False)


class CreateBoardColumnSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    color = serializers.CharField(max_length=7, required=False, default="", allow_blank=True)
    wip_limit = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    position = serializers.IntegerField(required=False, allow_null=True, min_value=0)


class UpdateBoardColumnSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    color = serializers.CharField(max_length=7, required=False, allow_blank=True)
    wip_limit = serializers.IntegerField(required=False, allow_null=True, min_value=1)


class ReorderColumnsSerializer(serializers.Serializer):
    ordered_column_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of column UUIDs in the desired display order.",
    )

