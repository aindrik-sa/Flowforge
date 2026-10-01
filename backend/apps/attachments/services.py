import mimetypes

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.attachments.models import Attachment
from apps.tasks.models import Task, TaskActivityLog
from apps.tasks.services import _log_activity


# Maximum upload size: 25 MB
MAX_UPLOAD_SIZE = 25 * 1024 * 1024

# Allowed MIME types
ALLOWED_CONTENT_TYPES = {
    # Images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # Spreadsheets
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # Presentations
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    # Archives
    "application/zip",
    "application/x-rar-compressed",
    # Text
    "text/plain",
    "text/csv",
    "application/json",
}


def create_attachment(
    *,
    task: Task,
    file: UploadedFile,
    uploaded_by,
) -> Attachment:
    """
    Upload a file attachment to a task.

    WHAT: Validates file size and type, persists the file, and logs activity.
    WHY:  Centralizing validation here prevents oversized or dangerous files
          from reaching storage, regardless of which endpoint is used.
    IMPORTANT:
      - Content type is determined server-side using mimetypes, not from
        the client-provided Content-Type header (security best practice).
      - File size is read from the uploaded file object, not from client headers.
    """
    # Validate file size
    if file.size > MAX_UPLOAD_SIZE:
        raise ValueError(
            f"File size ({file.size} bytes) exceeds the maximum "
            f"allowed size ({MAX_UPLOAD_SIZE} bytes / 25 MB)."
        )

    # Determine content type server-side
    content_type, _ = mimetypes.guess_type(file.name)
    content_type = content_type or "application/octet-stream"

    # Validate content type
    if content_type not in ALLOWED_CONTENT_TYPES and content_type != "application/octet-stream":
        raise ValueError(
            f"File type '{content_type}' is not allowed. "
            f"Allowed types include images, PDFs, Office documents, and archives."
        )

    with transaction.atomic():
        attachment = Attachment.objects.create(
            task=task,
            file=file,
            original_filename=file.name,
            file_size=file.size,
            content_type=content_type,
            uploaded_by=uploaded_by,
        )

        _log_activity(
            task=task,
            action=TaskActivityLog.Action.UPDATED,
            changed_by=uploaded_by,
            field_name="attachment",
            new_value=file.name,
        )

    return attachment


def delete_attachment(*, attachment: Attachment) -> None:
    """
    Delete an attachment and remove the file from storage.

    WHAT: Deletes the database record and the physical file.
    WHY:  Orphaned files waste storage. Clean up on delete.
    """
    # Delete the physical file
    if attachment.file:
        attachment.file.delete(save=False)

    attachment.delete()
