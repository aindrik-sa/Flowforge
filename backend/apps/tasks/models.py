from django.conf import settings
from django.db import models

from apps.common.models import BaseModel
from apps.projects.models import Project, BoardColumn


class TaskLabel(BaseModel):
    """
    Reusable label scoped to a project.

    WHAT: A colored tag like "bug", "feature", "urgent" that can be
          attached to any task in the same project.
    WHY:  Labels are project-scoped (not global) so different projects
          can maintain independent taxonomies.
    IMPORTANT: The (project, name) pair is unique — no duplicate label
               names within a project.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="labels",
    )
    name = models.CharField(max_length=50)
    color = models.CharField(
        max_length=7,
        default="#6B7280",
        help_text="Hex color code for UI rendering (e.g. #EF4444).",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="unique_label_name_per_project",
            ),
        ]

    def __str__(self):
        return f"{self.project.key}: {self.name}"


class Task(BaseModel):
    """
    A work item on a Kanban board.

    WHAT: The core entity of project management — a unit of work with
          priority, assignees, due dates, and position on a board column.
    WHY:  Tasks live inside a BoardColumn for Kanban display, but also
          link to the Project directly for cross-board queries and
          task numbering (e.g. FLOW-42).
    IMPORTANT:
      - `task_number` is auto-incremented per project by the service layer.
        Never set it manually.
      - `position` determines vertical order within a column.
        Use the service layer's reorder/move functions to change it.
    """

    class Priority(models.TextChoices):
        URGENT = "urgent", "Urgent"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"
        NONE = "none", "None"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    column = models.ForeignKey(
        BoardColumn,
        on_delete=models.PROTECT,
        related_name="tasks",
        help_text="The board column this task currently sits in.",
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")
    task_number = models.PositiveIntegerField(
        help_text="Auto-incremented per project (e.g. 42 in FLOW-42).",
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated effort in hours.",
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Vertical order within the column. Lower = higher on the board.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_tasks",
        help_text="The user who created/reported this task.",
    )
    labels = models.ManyToManyField(
        TaskLabel,
        blank=True,
        related_name="tasks",
    )

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "task_number"],
                name="unique_task_number_per_project",
            ),
        ]

    def __str__(self):
        return f"{self.project.key}-{self.task_number}: {self.title}"

    @property
    def identifier(self) -> str:
        """Human-readable task identifier, e.g. FLOW-42."""
        return f"{self.project.key}-{self.task_number}"


class TaskAssignment(BaseModel):
    """
    Links a user to a task as an assignee.

    WHAT: Many-to-many relationship between Tasks and Users.
    WHY:  A task can have multiple assignees (pair programming, shared
          ownership). Using an explicit through model lets us track
          when the assignment was made.
    IMPORTANT: (task, user) is unique — can't assign the same person twice.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_assignments",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["assigned_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "user"],
                name="unique_task_assignment",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.task.identifier}"


class TaskActivityLog(BaseModel):
    """
    Immutable audit trail for task changes.

    WHAT: Records every meaningful change made to a task — field name,
          old value, new value, and who made the change.
    WHY:  Activity logs are critical for accountability, debugging, and
          the task detail page's "Activity" tab.
    IMPORTANT: These are append-only. Never update or delete activity logs.
    """

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        MOVED = "moved", "Moved"
        ASSIGNED = "assigned", "Assigned"
        UNASSIGNED = "unassigned", "Unassigned"
        LABEL_ADDED = "label_added", "Label Added"
        LABEL_REMOVED = "label_removed", "Label Removed"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
    )
    field_name = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="The field that was changed (e.g. 'priority', 'column').",
    )
    old_value = models.TextField(
        blank=True,
        default="",
        help_text="Previous value (stringified).",
    )
    new_value = models.TextField(
        blank=True,
        default="",
        help_text="New value (stringified).",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="task_activity_logs",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task.identifier} — {self.action} by {self.changed_by.email}"
