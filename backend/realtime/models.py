import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Persistent notification for a user.

    Created by the signal handler for every workflow event.
    Delivered in real-time via SSE to online users, and fetched
    via REST API for offline users on next login.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    event_type = models.CharField(max_length=50)
    # The proposal this notification is about
    request_ref = models.ForeignKey(
        "proposals.Request",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    action = models.CharField(max_length=50)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )
    title = models.CharField(max_length=255, blank=True, default="")
    from_status = models.CharField(max_length=30, blank=True, null=True)
    to_status = models.CharField(max_length=30, blank=True, null=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "read"]),
        ]

    def __str__(self):
        return f"Notification({self.event_type} → {self.recipient})"
