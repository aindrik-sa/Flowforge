from django.contrib.auth import get_user_model
from django.db import transaction

from apps.comments.models import Comment
from apps.tasks.models import Task, TaskActivityLog
from apps.tasks.services import _log_activity

User = get_user_model()


def _resolve_mentions(comment: Comment) -> None:
    """
    Parse @email mentions from the comment body and populate
    the mentions M2M field with matching users.
    """
    emails = Comment.extract_mentions(comment.body)
    if emails:
        mentioned_users = User.objects.filter(email__in=emails)
        comment.mentions.set(mentioned_users)
    else:
        comment.mentions.clear()


def create_comment(
    *,
    task: Task,
    author,
    body: str,
    parent: Comment = None,
) -> Comment:
    """
    Create a comment on a task.

    WHAT: Creates the comment, resolves @mentions, and logs activity.
    WHY:  Comments are the primary collaboration tool. Mentions
          enable targeted notifications (future sprint).
    IMPORTANT: If `parent` is provided, it must belong to the same task.
    """
    if parent and parent.task_id != task.id:
        raise ValueError("Parent comment must belong to the same task.")

    with transaction.atomic():
        comment = Comment.objects.create(
            task=task,
            author=author,
            body=body,
            parent=parent,
        )

        _resolve_mentions(comment)

        _log_activity(
            task=task,
            action=TaskActivityLog.Action.UPDATED,
            changed_by=author,
            field_name="comment",
            new_value=body[:100],
        )

    return comment


def update_comment(
    *,
    comment: Comment,
    body: str,
    updated_by,
) -> Comment:
    """
    Update a comment's body.

    WHAT: Updates the body, re-resolves mentions, and marks as edited.
    WHY:  Users often fix typos or add context after posting.
    IMPORTANT: Only the comment author can edit (enforced at view level).
    """
    if comment.body == body:
        return comment

    with transaction.atomic():
        comment.body = body
        comment.is_edited = True
        comment.save(update_fields=["body", "is_edited", "updated_at"])

        _resolve_mentions(comment)

    return comment


def delete_comment(*, comment: Comment) -> None:
    """
    Delete a comment.

    WHAT: Removes the comment and all its replies (CASCADE).
    WHY:  When a parent comment is deleted, child replies lose context
          and should be removed too.
    """
    comment.delete()
