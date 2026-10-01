from apps.tasks.models import Task, TaskLabel, TaskAssignment, TaskActivityLog
from apps.projects.models import Project, BoardColumn


def get_project_tasks(*, project: Project):
    """
    Return all tasks in a project, with assignments and labels prefetched.
    """
    return (
        Task.objects.filter(project=project)
        .select_related("column", "created_by")
        .prefetch_related("assignments__user", "labels")
        .order_by("column__position", "position")
    )


def get_column_tasks(*, column: BoardColumn):
    """Return all tasks in a specific board column, ordered by position."""
    return (
        Task.objects.filter(column=column)
        .select_related("created_by")
        .prefetch_related("assignments__user", "labels")
        .order_by("position")
    )


def get_task_detail(*, task_id):
    """
    Retrieve a single task with all related data prefetched.
    Returns None if not found.
    """
    try:
        return (
            Task.objects.select_related(
                "project__workspace__organization",
                "column__board",
                "created_by",
            )
            .prefetch_related("assignments__user", "labels")
            .get(pk=task_id)
        )
    except Task.DoesNotExist:
        return None


def get_task_assignments(*, task: Task):
    """Return all assignments for a task."""
    return TaskAssignment.objects.filter(task=task).select_related("user")


def get_task_activity(*, task: Task):
    """Return the activity log for a task, most recent first."""
    return (
        TaskActivityLog.objects.filter(task=task)
        .select_related("changed_by")
        .order_by("-created_at")
    )


def get_project_labels(*, project: Project):
    """Return all labels for a project."""
    return TaskLabel.objects.filter(project=project)
