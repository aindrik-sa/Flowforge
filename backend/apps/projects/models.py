from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import BaseModel
from apps.organizations.models import Organization


class Workspace(BaseModel):
    """
    Workspaces organize projects within an organization.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="workspaces",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_workspace_name_per_org",
            ),
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_workspace_slug_per_org",
            ),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(BaseModel):
    """
    Projects contain boards and tasks.
    """

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=255)
    key = models.CharField(
        max_length=10,
        help_text="Short key for issue tracking (e.g. FLOW-1).",
    )
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_projects",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "key"],
                name="unique_project_key_per_workspace",
            ),
            models.UniqueConstraint(
                fields=["workspace", "slug"],
                name="unique_project_slug_per_workspace",
            ),
        ]

    def __str__(self):
        return f"[{self.key}] {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.key:
            self.key = self.key.upper()
        super().save(*args, **kwargs)


class ProjectMember(BaseModel):
    """
    Membership linking a User to a Project.
    """

    class Role(models.TextChoices):
        MANAGER = "manager", "Manager"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_member",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.project.name} ({self.role})"


class Board(BaseModel):
    """
    A Kanban board within a project.

    WHAT: Groups columns (and eventually tasks/cards) into a visual workflow.
    WHY:  A project may need multiple boards (e.g. one per sprint, or
          separate boards for different workflows like "Bug Triage" vs "Features").
    IMPORTANT: When a board is created via the service layer, it automatically
               gets 5 default columns (Backlog → To Do → In Progress → Review → Done).
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="boards",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_default = models.BooleanField(
        default=False,
        help_text="If True, this board is the one displayed first in the UI.",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "slug"],
                name="unique_board_slug_per_project",
            ),
        ]

    def __str__(self):
        return f"{self.project.name} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BoardColumn(BaseModel):
    """
    An ordered column within a Kanban board.

    WHAT: Represents a workflow stage (e.g. "In Progress", "Done").
    WHY:  Columns have an explicit `position` field so the frontend can
          render them left-to-right and users can reorder via drag-and-drop.
    IMPORTANT: Always use the service layer's `reorder_columns()` to change
               positions — never set `position` directly, as it must remain
               unique within a board.
    """

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="columns",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    position = models.PositiveIntegerField(
        help_text="Zero-based display order. Lower = further left.",
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Hex color code for UI rendering (e.g. #4CAF50).",
    )
    wip_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of cards allowed in this column (optional).",
    )

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["board", "slug"],
                name="unique_column_slug_per_board",
            ),
            models.UniqueConstraint(
                fields=["board", "position"],
                name="unique_column_position_per_board",
            ),
        ]

    def __str__(self):
        return f"{self.board.name} — {self.name} (pos {self.position})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
