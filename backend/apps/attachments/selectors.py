from apps.attachments.models import Attachment
from apps.tasks.models import Task


def get_task_attachments(*, task: Task):
    """Return all attachments for a task, with uploader prefetched."""
    return (
        Attachment.objects.filter(task=task)
        .select_related("uploaded_by")
        .order_by("-created_at")
    )


def get_attachment_detail(*, attachment_id):
    """Retrieve a single attachment with related data. Returns None if not found."""
    try:
        return (
            Attachment.objects.select_related(
                "task__project__workspace__organization",
                "uploaded_by",
            ).get(pk=attachment_id)
        )
    except Attachment.DoesNotExist:
        return None
