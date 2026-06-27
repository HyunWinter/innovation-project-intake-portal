import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .request import Request


class CommentManager(models.Manager):
    """Custom manager that hides soft deleted rows
    The default manager will be used for viewing all rows
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Comment(models.Model):
    """A free-text comment on a request."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete

    objects = CommentManager()  # hides soft-deleted rows
    all_objects = models.Manager()  # includes soft-deleted rows

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.request_id}"

    def delete(self, using=None, keep_parents=False):
        """Soft delete: stamp ``deleted_at`` instead of removing the row."""
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["deleted_at"])
