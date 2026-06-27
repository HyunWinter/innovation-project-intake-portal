import uuid

from django.conf import settings
from django.db import models

from ..enums import Status
from .request import Request


class AuditEvent(models.Model):
    """Typed audit-trail entity
    One row written per transition
    This should never be updated or deleted
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="audit_events")
    # Null if the actor's account is later removed
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_events",
    )
    event_type = models.CharField(max_length=50)  # transition or action name
    from_status = models.CharField(max_length=20, choices=Status.choices, null=True, blank=True)
    to_status = models.CharField(max_length=20, choices=Status.choices, null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.event_type} on {self.request_id}"
