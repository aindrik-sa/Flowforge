from django.contrib import admin

from apps.tasks.models import Task, TaskLabel, TaskAssignment, TaskActivityLog


class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 0
    readonly_fields = ("assigned_at",)
    raw_id_fields = ("user",)


class TaskActivityLogInline(admin.TabularInline):
    model = TaskActivityLog
    extra = 0
    readonly_fields = (
        "action",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "created_at",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "title",
        "project",
        "column",
        "priority",
        "position",
        "created_by",
        "created_at",
    )
    list_filter = ("priority", "project", "column__board")
    search_fields = ("title", "description", "project__key")
    readonly_fields = ("task_number", "created_at", "updated_at")
    raw_id_fields = ("project", "column", "created_by")
    inlines = [TaskAssignmentInline, TaskActivityLogInline]

    @admin.display(description="Identifier")
    def identifier(self, obj):
        return obj.identifier


@admin.register(TaskLabel)
class TaskLabelAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "color", "created_at")
    list_filter = ("project",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ("task", "user", "assigned_at")
    search_fields = ("task__title", "user__email")
    raw_id_fields = ("task", "user")
    readonly_fields = ("assigned_at", "created_at", "updated_at")


@admin.register(TaskActivityLog)
class TaskActivityLogAdmin(admin.ModelAdmin):
    list_display = ("task", "action", "field_name", "changed_by", "created_at")
    list_filter = ("action",)
    search_fields = ("task__title", "changed_by__email")
    readonly_fields = (
        "task",
        "action",
        "field_name",
        "old_value",
        "new_value",
        "changed_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
