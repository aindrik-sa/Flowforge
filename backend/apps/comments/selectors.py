from apps.comments.models import Comment
from apps.tasks.models import Task


def get_task_comments(*, task: Task):
    """
    Return top-level comments for a task, with replies and mentions prefetched.

    WHY: Only fetch top-level comments (parent=None) and nest replies via
         prefetch. This gives a threaded view without multiple queries.
    """
    return (
        Comment.objects.filter(task=task, parent__isnull=True)
        .select_related("author")
        .prefetch_related(
            "replies__author",
            "replies__mentions",
            "mentions",
        )
        .order_by("created_at")
    )


def get_comment_detail(*, comment_id):
    """Retrieve a single comment with related data. Returns None if not found."""
    try:
        return (
            Comment.objects.select_related(
                "task__project__workspace__organization",
                "author",
                "parent",
            )
            .prefetch_related("mentions", "replies__author")
            .get(pk=comment_id)
        )
    except Comment.DoesNotExist:
        return None


def get_task_comment_count(*, task: Task) -> int:
    """Return the total number of comments on a task."""
    return Comment.objects.filter(task=task).count()
