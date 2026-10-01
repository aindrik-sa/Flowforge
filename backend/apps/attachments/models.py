import os

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel
from apps.tasks.models import Task


def attachment_upload_path(instance, filename):
    """
    Generate upload path: attachments/<project_key>/<task_number>/<filename>

    WHY: Organizing files by project and task makes it easy to browse
         uploads on disk and simplifies backup/cleanup operations.
    """
    task = instance.task
    return os.path.join(
        "attachments",
        task.project.key.lower(),
        str(task.task_number),
        filename,
    )


class Attachment(BaseModel):
    """
    A file uploaded to a task.

    WHAT: Supports images, PDFs, documents, spreadsheets, and other files
          attached to a task for reference or collaboration.
    WHY:  Team members need to share screenshots, specs, design files, etc.
          directly in the context of the task they relate to.
    IMPORTANT:
      - `original_filename` preserves the user's filename even if the
        storage backend renames the file for uniqueness.
      - `file_size` and `content_type` are captured at upload time by
        the service layer — never trust client-provided values.
      - File size limits should be enforced in settings/views, not here.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        upload_to=attachment_upload_path,
    )
    original_filename = models.CharField(
        max_length=255,
        help_text="Original name of the uploaded file.",
    )
    file_size = models.PositiveIntegerField(
        help_text="File size in bytes.",
    )
    content_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="MIME type (e.g. image/png, application/pdf).",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_attachments",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.original_filename} on {self.task.identifier}"

    @property
    def file_extension(self) -> str:
        """Return the file extension (e.g. '.pdf')."""
        _, ext = os.path.splitext(self.original_filename)
        return ext.lower()

    @property
    def is_image(self) -> bool:
        """Check if the attachment is an image based on content type."""
        return self.content_type.startswith("image/")
