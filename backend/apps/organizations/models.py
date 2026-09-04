from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import BaseModel


class Organization(BaseModel):
    """
    The top-level tenant boundary in FlowForge.

    WHAT: Represents a company/team that owns workspaces, projects, and tasks.
    WHY:  Multi-tenancy — every piece of data belongs to an organization.
          Users see only data from organizations they belong to.
    IMPORTANT: Always filter querysets by organization to prevent data leakage.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
        help_text="The user who created and owns this organization.",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class OrganizationMember(BaseModel):
    """
    Membership linking a User to an Organization with a specific role.

    WHAT: Many-to-many relationship between Users and Organizations with role metadata.
    WHY:  A user can belong to multiple organizations with different roles.
          John can be an admin at Microsoft and a member at StartupX.
          The role belongs to the membership, NOT to the user.
    IMPORTANT: Never put organization-specific role on the User model.
               Always check membership when authorizing organization actions.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_organization_member",
            ),
        ]
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.email} → {self.organization.name} ({self.role})"
