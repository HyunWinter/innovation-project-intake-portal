"""Signal handler: post_transition → SSE event bus + DB persistence

Translates Django signal kwargs into a JSON serializable event and
publishes it to all connected SSE clients. Also persists a
Notification row per recipient so offline users see it on login.
"""

from django.utils import timezone

from proposals.models import AuditEvent, Comment

from . import bus
from .models import Notification
from .signals import post_transition


def _get_related_user_ids(request_obj, exclude_actor_id):
    """Return the set of user IDs related to a proposal, minus the actor"""
    user_ids = set()

    # 1. Submitter is always related
    user_ids.add(str(request_obj.submitter_id))

    # 2. Anyone who has taken an action (AuditEvent actors)
    audit_actor_ids = (
        AuditEvent.objects.filter(request=request_obj).values_list("actor_id", flat=True).distinct()
    )
    user_ids.update(str(uid) for uid in audit_actor_ids)

    # 3. Anyone who has commented
    comment_author_ids = (
        Comment.objects.filter(request=request_obj).values_list("author_id", flat=True).distinct()
    )
    user_ids.update(str(uid) for uid in comment_author_ids)

    # Exclude the actor who triggered this event
    user_ids.discard(str(exclude_actor_id))

    return user_ids


def _on_post_transition(sender, **kwargs):
    """Handle post_transition signal: persist to DB + push to SSE"""
    request_obj = kwargs["request_obj"]
    action = kwargs["action"]
    from_status = kwargs.get("from_status")
    to_status = kwargs.get("to_status")
    actor = kwargs["actor"]

    # Determine event type
    if action == "create":
        event_type = "proposal_created"
    elif action == "comment":
        event_type = "comment_added"
    elif action == "resubmit":
        event_type = "proposal_resubmitted"
    else:
        event_type = "proposal_updated"

    # Build the set of users who should be notified
    target_user_ids = _get_related_user_ids(request_obj, actor.id)

    if not target_user_ids:
        return

    import uuid

    # 1. Persist to DB (one row per recipient)
    notifications = []
    for uid in target_user_ids:
        notifications.append(
            Notification(
                id=uuid.uuid4(),
                recipient_id=uid,
                event_type=event_type,
                request_ref=request_obj,
                action=action,
                actor=actor,
                title=getattr(request_obj, "title", ""),
                from_status=from_status,
                to_status=to_status,
            )
        )
    Notification.objects.bulk_create(notifications)

    # Map user_id -> notification_id
    user_to_notif_id = {str(n.recipient_id): str(n.id) for n in notifications}

    # 2. Push to SSE bus (for online users)
    event = {
        "type": event_type,
        "target_user_ids": target_user_ids,
        "user_to_notif_id": user_to_notif_id,
        "data": {
            "request_id": str(request_obj.id),
            "title": getattr(request_obj, "title", ""),
            "action": action,
            "from_status": from_status,
            "to_status": to_status,
            "actor_name": actor.name if hasattr(actor, "name") else str(actor),
            "actor_id": str(actor.id),
            "timestamp": timezone.now().isoformat(),
        },
    }

    bus.publish(event)


post_transition.connect(_on_post_transition)
