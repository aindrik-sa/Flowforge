from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from apps.notifications.models import Notification
from apps.notifications.tasks import send_email_notification_task


def create_notification(
    *,
    recipient,
    actor=None,
    verb: str,
    target=None,
    send_email: bool = False,
) -> Notification:
    """
    Create a notification and broadcast it via WebSockets.

    WHAT: Saves a notification to the DB, fires a WebSocket event,
          and optionally queues an email task.
    WHY:  Centralizes the alerting logic.
    """
    with transaction.atomic():
        notification = Notification.objects.create(
            recipient=recipient,
            actor=actor,
            verb=verb,
            target=target,
        )

    # Prepare payload for WebSockets
    payload = {
        "id": str(notification.id),
        "verb": notification.verb,
        "actor": getattr(actor, "email", "System"),
        "is_read": False,
        "created_at": notification.created_at.isoformat(),
    }

    # Broadcast via WebSockets
    channel_layer = get_channel_layer()
    group_name = f"user_notifications_{recipient.id}"
    
    # We use async_to_sync because this service function is synchronous
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "notify",
            "payload": payload,
        }
    )

    # Queue an email if requested
    if send_email:
        # Avoid passing complex Django objects to Celery tasks; pass IDs instead
        actor_id = actor.id if actor else None
        target_ct_id = notification.target_content_type_id if target else None
        target_obj_id = str(notification.target_object_id) if target else None
        
        send_email_notification_task.delay(
            recipient_id=recipient.id,
            actor_id=actor_id,
            verb=verb,
            target_ct_id=target_ct_id,
            target_obj_id=target_obj_id,
        )

    return notification


def mark_as_read(*, notification: Notification) -> Notification:
    """Mark a notification as read."""
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
    return notification


def mark_all_as_read(*, user) -> None:
    """Mark all notifications as read for a given user."""
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)
