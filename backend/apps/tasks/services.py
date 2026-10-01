from django.db import models, transaction
from django.utils.text import slugify

from apps.tasks.models import (
    Task,
    TaskLabel,
    TaskAssignment,
    TaskActivityLog,
)
from apps.projects.models import Project, BoardColumn


# ---------------------------------------------------------------------------
# Task Services
# ---------------------------------------------------------------------------


def _next_task_number(project: Project) -> int:
    """Return the next available task number for a project."""
    max_number = (
        Task.objects.filter(project=project)
        .aggregate(max_num=models.Max("task_number"))
        .get("max_num")
    )
    return (max_number or 0) + 1


def _next_position(column: BoardColumn) -> int:
    """Return the next position at the bottom of a column."""
    return Task.objects.filter(column=column).count()


def _log_activity(
    *,
    task: Task,
    action: str,
    changed_by,
    field_name: str = "",
    old_value: str = "",
    new_value: str = "",
) -> TaskActivityLog:
    """Create an activity log entry for a task."""
    return TaskActivityLog.objects.create(
        task=task,
        action=action,
        field_name=field_name,
        old_value=str(old_value),
        new_value=str(new_value),
        changed_by=changed_by,
    )


def create_task(
    *,
    project: Project,
    column: BoardColumn,
    title: str,
    created_by,
    description: str = "",
    priority: str = Task.Priority.MEDIUM,
    due_date=None,
    start_date=None,
    estimated_hours=None,
) -> Task:
    """
    Create a new task within a project and board column.

    WHAT: Creates the task, auto-assigns task_number, places it at the
          bottom of the column, and logs a "created" activity entry.
    WHY:  Task number and position must be calculated atomically to avoid
          race conditions with concurrent task creation.
    """
    with transaction.atomic():
        task_number = _next_task_number(project)
        position = _next_position(column)

        task = Task.objects.create(
            project=project,
            column=column,
            title=title,
            description=description,
            task_number=task_number,
            priority=priority,
            due_date=due_date,
            start_date=start_date,
            estimated_hours=estimated_hours,
            position=position,
            created_by=created_by,
        )

        _log_activity(
            task=task,
            action=TaskActivityLog.Action.CREATED,
            changed_by=created_by,
            new_value=title,
        )

    return task


def update_task(
    *,
    task: Task,
    updated_by,
    **fields,
) -> Task:
    """
    Update task fields and log each change to the activity log.

    WHAT: Accepts arbitrary field updates, compares old vs new, and
          creates an activity entry for every changed field.
    WHY:  Granular activity logging — users see exactly what changed,
          when, and by whom.
    """
    updatable_fields = {
        "title", "description", "priority",
        "due_date", "start_date", "estimated_hours",
    }

    changed = []
    with transaction.atomic():
        for field_name, new_value in fields.items():
            if field_name not in updatable_fields:
                continue

            old_value = getattr(task, field_name)
            if old_value != new_value:
                setattr(task, field_name, new_value)
                changed.append(field_name)

                _log_activity(
                    task=task,
                    action=TaskActivityLog.Action.UPDATED,
                    changed_by=updated_by,
                    field_name=field_name,
                    old_value=old_value if old_value is not None else "",
                    new_value=new_value if new_value is not None else "",
                )

        if changed:
            task.save(update_fields=changed + ["updated_at"])

    return task


def move_task(
    *,
    task: Task,
    target_column: BoardColumn,
    position: int = None,
    moved_by,
) -> Task:
    """
    Move a task to a different column (and optionally to a specific position).

    WHAT: Removes the task from its current column, re-normalizes the old
          column's positions, inserts it into the target column at the
          specified position (or at the bottom), and logs the move.
    WHY:  Drag-and-drop on the Kanban board = moving cards between columns.
    """
    old_column = task.column

    with transaction.atomic():
        # Remove from old column — shift positions down
        if old_column.id != target_column.id:
            tasks_after = list(
                Task.objects.filter(
                    column=old_column, position__gt=task.position
                ).order_by("position")
            )
            for t in tasks_after:
                t.position -= 1
                t.save(update_fields=["position"])

        # Determine target position
        if position is None:
            position = Task.objects.filter(column=target_column).exclude(
                id=task.id
            ).count()

        # Shift tasks in target column to make room
        if old_column.id != target_column.id:
            tasks_to_shift = list(
                Task.objects.filter(
                    column=target_column, position__gte=position
                ).order_by("-position")
            )
        else:
            # Moving within the same column
            if position > task.position:
                # Moving down — shift tasks between old and new position up
                tasks_to_shift = list(
                    Task.objects.filter(
                        column=target_column,
                        position__gt=task.position,
                        position__lte=position,
                    ).exclude(id=task.id).order_by("position")
                )
                for t in tasks_to_shift:
                    t.position -= 1
                    t.save(update_fields=["position"])
                tasks_to_shift = []  # Already handled
            elif position < task.position:
                # Moving up — shift tasks between new and old position down
                tasks_to_shift = list(
                    Task.objects.filter(
                        column=target_column,
                        position__gte=position,
                        position__lt=task.position,
                    ).exclude(id=task.id).order_by("-position")
                )
            else:
                tasks_to_shift = []

        for t in tasks_to_shift:
            t.position += 1
            t.save(update_fields=["position"])

        task.column = target_column
        task.position = position
        task.save(update_fields=["column", "position", "updated_at"])

        if old_column.id != target_column.id:
            _log_activity(
                task=task,
                action=TaskActivityLog.Action.MOVED,
                changed_by=moved_by,
                field_name="column",
                old_value=old_column.name,
                new_value=target_column.name,
            )

    return task


def reorder_tasks(
    *,
    column: BoardColumn,
    ordered_task_ids: list,
) -> None:
    """
    Reorder tasks within a column by setting positions based on the
    order of IDs provided.

    WHAT: Accepts a list of task UUIDs in the desired display order.
    WHY:  Drag-and-drop reordering within a single column.
    IMPORTANT: All task IDs for the column must be included.
    """
    existing_ids = set(
        Task.objects.filter(column=column).values_list("id", flat=True)
    )
    provided_ids = set(ordered_task_ids)

    if existing_ids != provided_ids:
        raise ValueError(
            "The provided task IDs do not match the column's tasks. "
            "All tasks must be included, with no extras."
        )

    with transaction.atomic():
        # Two-pass update to avoid unique constraint violations
        for idx, task_id in enumerate(ordered_task_ids):
            Task.objects.filter(id=task_id).update(position=100000 + idx)

        for idx, task_id in enumerate(ordered_task_ids):
            Task.objects.filter(id=task_id).update(position=idx)


# ---------------------------------------------------------------------------
# Assignment Services
# ---------------------------------------------------------------------------


def assign_task(
    *,
    task: Task,
    user,
    assigned_by,
) -> TaskAssignment:
    """Assign a user to a task."""
    assignment = TaskAssignment.objects.create(
        task=task,
        user=user,
    )

    _log_activity(
        task=task,
        action=TaskActivityLog.Action.ASSIGNED,
        changed_by=assigned_by,
        field_name="assignee",
        new_value=user.email,
    )

    return assignment


def unassign_task(
    *,
    task: Task,
    user,
    removed_by,
) -> None:
    """Remove a user's assignment from a task."""
    assignment = TaskAssignment.objects.filter(task=task, user=user)
    deleted_count, _ = assignment.delete()

    if deleted_count == 0:
        raise ValueError("User is not assigned to this task.")

    _log_activity(
        task=task,
        action=TaskActivityLog.Action.UNASSIGNED,
        changed_by=removed_by,
        field_name="assignee",
        old_value=user.email,
    )


# ---------------------------------------------------------------------------
# Label Services
# ---------------------------------------------------------------------------


def create_label(
    *,
    project: Project,
    name: str,
    color: str = "#6B7280",
) -> TaskLabel:
    """Create a new label within a project."""
    return TaskLabel.objects.create(
        project=project,
        name=name,
        color=color,
    )


def add_label_to_task(
    *,
    task: Task,
    label: TaskLabel,
    added_by,
) -> None:
    """Attach a label to a task."""
    task.labels.add(label)

    _log_activity(
        task=task,
        action=TaskActivityLog.Action.LABEL_ADDED,
        changed_by=added_by,
        field_name="label",
        new_value=label.name,
    )


def remove_label_from_task(
    *,
    task: Task,
    label: TaskLabel,
    removed_by,
) -> None:
    """Remove a label from a task."""
    task.labels.remove(label)

    _log_activity(
        task=task,
        action=TaskActivityLog.Action.LABEL_REMOVED,
        changed_by=removed_by,
        field_name="label",
        old_value=label.name,
    )
