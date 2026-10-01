from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.tasks.models import Task, TaskLabel, TaskAssignment, TaskActivityLog

User = get_user_model()


# ---------------------------------------------------------------------------
# Label Serializers
# ---------------------------------------------------------------------------


class TaskLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLabel
        fields = (
            "id",
            "name",
            "color",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CreateTaskLabelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    color = serializers.CharField(max_length=7, required=False, default="#6B7280")


# ---------------------------------------------------------------------------
# Assignment Serializers
# ---------------------------------------------------------------------------


class TaskAssignmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TaskAssignment
        fields = (
            "id",
            "user",
            "assigned_at",
        )
        read_only_fields = fields


class AssignTaskSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        email = value.lower().strip()
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return email


# ---------------------------------------------------------------------------
# Task Serializers
# ---------------------------------------------------------------------------


class TaskSerializer(serializers.ModelSerializer):
    """Read serializer for tasks with nested assignments and labels."""

    created_by = UserSerializer(read_only=True)
    assignments = TaskAssignmentSerializer(many=True, read_only=True)
    labels = TaskLabelSerializer(many=True, read_only=True)
    identifier = serializers.CharField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "project",
            "column",
            "title",
            "description",
            "task_number",
            "identifier",
            "priority",
            "due_date",
            "start_date",
            "estimated_hours",
            "position",
            "created_by",
            "assignments",
            "labels",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists (no full nested data)."""

    identifier = serializers.CharField(read_only=True)
    assignee_count = serializers.SerializerMethodField()
    label_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "column",
            "title",
            "task_number",
            "identifier",
            "priority",
            "due_date",
            "position",
            "assignee_count",
            "label_count",
            "created_at",
        )
        read_only_fields = fields

    def get_assignee_count(self, obj):
        return obj.assignments.count()

    def get_label_count(self, obj):
        return obj.labels.count()


class CreateTaskSerializer(serializers.Serializer):
    column_id = serializers.UUIDField()
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    priority = serializers.ChoiceField(
        choices=Task.Priority.choices,
        default=Task.Priority.MEDIUM,
    )
    due_date = serializers.DateField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class UpdateTaskSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=Task.Priority.choices, required=False)
    due_date = serializers.DateField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class MoveTaskSerializer(serializers.Serializer):
    column_id = serializers.UUIDField()
    position = serializers.IntegerField(required=False, allow_null=True, min_value=0)


class ReorderTasksSerializer(serializers.Serializer):
    ordered_task_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of task UUIDs in the desired display order.",
    )


class AddLabelToTaskSerializer(serializers.Serializer):
    label_id = serializers.UUIDField()


# ---------------------------------------------------------------------------
# Activity Log Serializer
# ---------------------------------------------------------------------------


class TaskActivityLogSerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = TaskActivityLog
        fields = (
            "id",
            "action",
            "field_name",
            "old_value",
            "new_value",
            "changed_by",
            "created_at",
        )
        read_only_fields = fields
