import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(name="notifications.send_email")
def send_email_notification_task(
    recipient_id: str,
    actor_id: str | None,
    verb: str,
    target_ct_id: int | None = None,
    target_obj_id: str | None = None,
):
    """
    Background Celery task to send an email notification.
    
    Takes primitive IDs rather than Model instances to ensure safe
    serialization across the message broker (Redis).
    """
    try:
        recipient = User.objects.get(pk=recipient_id)
    except User.DoesNotExist:
        logger.warning(f"Recipient {recipient_id} not found. Aborting email.")
        return

    actor = None
    if actor_id:
        try:
            actor = User.objects.get(pk=actor_id)
        except User.DoesNotExist:
            pass

    target = None
    if target_ct_id and target_obj_id:
        try:
            ct = ContentType.objects.get(pk=target_ct_id)
            target = ct.get_object_for_this_type(pk=target_obj_id)
        except Exception as e:
            logger.warning(f"Failed to load target object: {e}")

    # Build the email
    actor_str = actor.email if actor else "System"
    target_str = str(target) if target else ""
    
    subject = f"FlowForge Notification: {actor_str} {verb}"
    message = (
        f"Hello {recipient.email},\n\n"
        f"{actor_str} {verb} {target_str}.\n\n"
        f"Thank you,\nThe FlowForge Team"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email="noreply@flowforge.internal",
        recipient_list=[recipient.email],
        fail_silently=False,
    )
    
    logger.info(f"Email sent successfully to {recipient.email}")
