import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from ..enums import (
    Category,
    CommitteeDecision,
    FundingStatus,
    PresentationStatus,
    Status,
    TechCategory,
)


class RequestManager(models.Manager):
    """Custom manager for hiding soft deleted rows
    For viewing all rows, you can use the default manager.
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Request(models.Model):
    """Innovation proposal and workflow state."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Workflow state (only by the state machine)
    category = models.CharField(max_length=1, choices=Category.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    committee_decision = models.CharField(
        max_length=30, choices=CommitteeDecision.choices, blank=True, default=""
    )
    presentation_status = models.CharField(
        max_length=20,
        choices=PresentationStatus.choices,
        default=PresentationStatus.NOT_REQUESTED,
    )
    # Create logic sets it to pending for Category B
    funding_status = models.CharField(
        max_length=20, choices=FundingStatus.choices, default=FundingStatus.NOT_REQUIRED
    )
    decision_reasoning = models.TextField(blank=True, default="")
    decision_made_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decisions_made",
    )
    decision_made_at = models.DateTimeField(null=True, blank=True)

    # Section 1: Prior-Art
    keywords = models.TextField(blank=True, default="")
    similar_projects_found = models.TextField(blank=True, default="")
    differentiation = models.TextField(blank=True, default="")
    collaboration_opportunities = models.TextField(blank=True, default="")

    # Section 2: Basic info
    contact_name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    site_or_team = models.CharField(max_length=255, blank=True, default="")
    tech_category = models.CharField(
        max_length=20, choices=TechCategory.choices, blank=True, default=""
    )
    collaboration_interest = models.BooleanField(default=False)

    # Section 3: Scope
    title = models.CharField(max_length=255)
    description = models.TextField()
    objectives = models.TextField()
    outcomes = models.TextField(blank=True, default="")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    phases = models.JSONField(default=list, blank=True)

    # Section 4: Resources
    funding_required = models.BooleanField(default=False)
    personnel = models.TextField(blank=True, default="")
    equipment = models.TextField(blank=True, default="")
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_roi = models.TextField(blank=True, default="")

    # Others: workflow related fields
    presentation_date = models.DateTimeField(null=True, blank=True)
    presentation_requirements = models.TextField(blank=True, default="")
    expected_resume_date = models.DateField(null=True, blank=True)
    suggested_collaborators = models.JSONField(null=True, blank=True)

    # Others: Ownership and dates
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # should soft delete

    objects = RequestManager()  # hides soft deleted rows
    all_objects = models.Manager()  # includes soft deleted rows

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def delete(self, using=None, keep_parents=False):
        """Soft delete override
        Hides the row instead of hard deleting it.
        Should work with both .delete() and queryset.delete().
        """
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["deleted_at"])
