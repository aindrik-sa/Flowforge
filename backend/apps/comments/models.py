import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from apps.common.models import BaseModel
from apps.tasks.models import Task


class Comment(BaseModel):
    """
    A discussion entry on a task.

    WHAT: A threaded comment with optional mentions and reply support.
    WHY:  Task discussions are the primary collaboration mechanism.
          Comments support threading via `parent` and user mentions
          via `@email` patterns in the body.
    IMPORTANT:
      - `is_edited` is set automatically when the body is updated
        via the service layer. Never set it directly.
      - `mentions` is populated automatically by parsing `@email`
        patterns from the body during creation/update.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comments",
    )
    body = models.TextField(
        help_text="Comment body. Use @email to mention users.",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        help_text="Parent comment for threading. Null = top-level comment.",
    )
    is_edited = models.BooleanField(
        default=False,
        help_text="Set to True when the comment body has been edited.",
    )
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="mentioned_in_comments",
        help_text="Users mentioned via @email in the comment body.",
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        truncated = self.body[:50] + "..." if len(self.body) > 50 else self.body
        return f"{self.author.email} on {self.task.identifier}: {truncated}"

    @staticmethod
    def extract_mentions(body: str) -> list[str]:
        """
        Extract email addresses from @mentions in the comment body.

        Matches patterns like @user@example.com in the text.
        Returns a list of unique, lowered email addresses.
        """
        # Match @user@domain.tld patterns
        pattern = r"@([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        emails = re.findall(pattern, body)
        return list(set(email.lower() for email in emails))
