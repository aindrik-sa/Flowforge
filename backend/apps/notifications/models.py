from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import BaseModel


class Notification(BaseModel):
    """
    In-app notification for a user.

    WHAT: A polymorphic notification pointing to any object (Task, Project, etc.)
          using GenericForeignKey.
    WHY:  Users need to be notified about assignments, mentions, and updates.
          Generic relations allow a single table to link to multiple target types.
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="actions",
        null=True,
        blank=True,
        help_text="The user who triggered the notification.",
    )
    verb = models.CharField(
        max_length=255,
        help_text="Action description (e.g. 'assigned you to', 'mentioned you in').",
    )

    # Generic Foreign Key to link to the target object (e.g. Task, Comment)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    target_object_id = models.UUIDField(null=True, blank=True)
    target = GenericForeignKey("target_content_type", "target_object_id")

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.verb}"
