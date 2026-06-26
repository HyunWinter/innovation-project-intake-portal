import uuid

from django.conf import settings
from django.db import models


class DraftRequest(models.Model):
    """Incomplete proposal submission

    Validated data when submitted
    TODO: Eventually, we want to purge this periodically so it does not
    bloat the Request table. Not needed at this point (expected max 200~300 drafts).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="drafts"
    )
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft by {self.author_id}"
