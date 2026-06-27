"""Workflow enums.

Separate from models.py so the workflow package can import them without
pulling in the models (which would be a circular import).
"""

from django.db import models


class Category(models.TextChoices):
    """A = no funding, B = funded.
    Comes from funding_required field"""

    A = "A", "A - No funding"
    B = "B", "B - Funding required"


class Status(models.TextChoices):
    """Request Statuses"""

    # Non-terminal states
    PENDING = "pending", "Pending"
    UNDER_REVIEW = "under_review", "Under review"
    APPROVED = "approved", "Approved"
    IN_PROGRESS = "in_progress", "In progress"
    ON_HOLD = "on_hold", "On hold"

    # Terminal states
    COMPLETED = "completed", "Completed"
    REJECTED = "rejected", "Rejected"
    MERGED = "merged", "Merged"


class CommitteeDecision(models.TextChoices):
    """The committee's decision on a request
    Changes are recorded in audit events
    """

    PROCEED_INDEPENDENTLY = "proceed_independently", "Proceed independently"
    COLLABORATION_RECOMMENDED = "collaboration_recommended", "Collaboration recommended"
    HOLD = "hold", "Hold"
    SEARCH_INSUFFICIENT = "search_insufficient", "Search insufficient"
    REQUEST_PRESENTATION = "request_presentation", "Request presentation"
    COMBINE_EXISTING = "combine_existing", "Combine with existing"
    ENHANCE_SEARCH = "enhance_search", "Enhance search"
    REJECT = "reject", "Reject"


class PresentationStatus(models.TextChoices):
    """Presentation sub flow
    (Category B only)
    """

    NOT_REQUESTED = "not_requested", "Not requested"
    REQUESTED = "requested", "Requested"
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"


class FundingStatus(models.TextChoices):
    """Default is not_required
    B -> pending -> approved or denied
    """

    NOT_REQUIRED = "not_required", "Not required"
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    DENIED = "denied", "Denied"


class TechCategory(models.TextChoices):
    """Submission tech area
    We can move this to a CMS field later if needed
    """

    AI_ML = "ai_ml", "AI / ML"
    AUTOMATION = "automation", "Automation"
    BUSINESS_PROCESS = "business_process", "Business process"
    OTHER = "other", "Other"
