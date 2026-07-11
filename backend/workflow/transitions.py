"""Transition registry for the workflow rules

References:
- [State Development](docs/STATE_DEVELOPMENT.md)
- [Workflow Readme](backend\workflow\README.md)
"""

from dataclasses import dataclass

from accounts.models import Role
from proposals.enums import (
    Category,
    CommitteeDecision,
    FundingStatus,
    PresentationStatus,
    Status,
)

ALL_ROLES = (Role.SUBMITTER, Role.COMMITTEE, Role.MANAGEMENT)

# Statuses
NON_TERMINAL = (
    Status.PENDING,
    Status.UNDER_REVIEW,
    Status.APPROVED,
    Status.IN_PROGRESS,
    Status.ON_HOLD,
)
TERMINAL = (Status.COMPLETED, Status.REJECTED, Status.MERGED)


# Immutable because we don't want to accidentally change the rules at runtime
@dataclass(frozen=True)
class Transition:
    action: str
    endpoint: str
    roles: tuple
    from_status: tuple
    to_status: Status | None = None
    category: Category | None = None
    require_presentation_status: tuple | None = None
    require_funding_status: tuple | None = None
    required_fields: tuple = ()
    set_committee_decision: CommitteeDecision | None = None
    set_presentation_status: PresentationStatus | None = None
    set_funding_status: FundingStatus | None = None
    terminal: bool = False


_TRANSITIONS = [
    # === Committee decision: Category A (no funding) ===
    # Pending -> Approved
    # Cleared for execution
    # Reasoning
    Transition(
        action="proceed_independently",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING,),
        category=Category.A,
        to_status=Status.APPROVED,
        required_fields=("decision_reasoning",),
        set_committee_decision=CommitteeDecision.PROCEED_INDEPENDENTLY,
    ),
    # Pending -> Approved
    # Connect to similar effort
    # Reasoning + suggested collaborators
    Transition(
        action="collaboration_recommended",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING,),
        category=Category.A,
        to_status=Status.APPROVED,
        required_fields=("decision_reasoning", "suggested_collaborators"),
        set_committee_decision=CommitteeDecision.COLLABORATION_RECOMMENDED,
    ),
    # Pending -> On hold
    # Overlapping effort in progress
    # Reasoning + expected resume date
    Transition(
        action="hold",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING,),
        category=Category.A,
        to_status=Status.ON_HOLD,
        required_fields=("decision_reasoning", "expected_resume_date"),
        set_committee_decision=CommitteeDecision.HOLD,
    ),
    # Pending -> Pending
    # Redo prior-art search
    # Reasoning
    Transition(
        action="search_insufficient",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING,),
        category=Category.A,
        to_status=Status.PENDING,
        required_fields=("decision_reasoning",),
        set_committee_decision=CommitteeDecision.SEARCH_INSUFFICIENT,
    ),
    # === Committee decision: Category B (funding required) ===
    # Pending / Under review -> Under review
    # Submitter must present
    # Reasoning + presentation requirements
    Transition(
        action="request_presentation",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING, Status.UNDER_REVIEW),
        category=Category.B,
        to_status=Status.UNDER_REVIEW,
        required_fields=("decision_reasoning", "presentation_requirements"),
        set_committee_decision=CommitteeDecision.REQUEST_PRESENTATION,
        set_presentation_status=PresentationStatus.REQUESTED,
    ),
    # Pending / Under review -> Merged
    # Merge with an existing funded project
    # Reasoning
    Transition(
        action="combine_existing",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING, Status.UNDER_REVIEW),
        category=Category.B,
        to_status=Status.MERGED,
        required_fields=("decision_reasoning", "merged_into"),
        set_committee_decision=CommitteeDecision.COMBINE_EXISTING,
        terminal=True,
    ),
    # Pending / Under review -> Pending
    # Redo search (funded path)
    # Reasoning
    Transition(
        action="enhance_search",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING, Status.UNDER_REVIEW),
        category=Category.B,
        to_status=Status.PENDING,
        required_fields=("decision_reasoning",),
        set_committee_decision=CommitteeDecision.ENHANCE_SEARCH,
    ),
    # === Committee decision: reject (both categories) ===
    # Pending / Under review -> Rejected
    # Terminal — No further action
    Transition(
        action="reject",
        endpoint="committee-decision",
        roles=(Role.COMMITTEE,),
        from_status=(Status.PENDING, Status.UNDER_REVIEW),
        to_status=Status.REJECTED,
        required_fields=("decision_reasoning",),
        set_committee_decision=CommitteeDecision.REJECT,
        terminal=True,
    ),
    # On hold -> Pending
    # Resume a held request
    Transition(
        action="resume",
        endpoint="resume",
        roles=(Role.COMMITTEE,),
        from_status=(Status.ON_HOLD,),
        to_status=Status.PENDING,
    ),
    # Presentation: Requested -> Scheduled
    # Set the presentation date
    # Presentation date
    Transition(
        action="schedule",
        endpoint="presentation",
        roles=(Role.COMMITTEE,),
        from_status=(Status.UNDER_REVIEW,),
        category=Category.B,
        require_presentation_status=(PresentationStatus.REQUESTED,),
        required_fields=("presentation_date",),
        set_presentation_status=PresentationStatus.SCHEDULED,
    ),
    # Presentation: Scheduled -> Completed
    # Proceeds to the funding decision
    Transition(
        action="advanced",
        endpoint="presentation-outcome",
        roles=(Role.COMMITTEE,),
        from_status=(Status.UNDER_REVIEW,),
        category=Category.B,
        require_presentation_status=(PresentationStatus.SCHEDULED,),
        set_presentation_status=PresentationStatus.COMPLETED,
    ),
    # Under review -> Rejected
    # Presentation not advanced
    Transition(
        action="not_advanced",
        endpoint="presentation-outcome",
        roles=(Role.COMMITTEE,),
        from_status=(Status.UNDER_REVIEW,),
        category=Category.B,
        require_presentation_status=(PresentationStatus.SCHEDULED,),
        to_status=Status.REJECTED,
        terminal=True,
    ),
    # Under review -> Approved
    # Funding approved
    Transition(
        action="go",
        endpoint="funding-decision",
        roles=(Role.MANAGEMENT,),
        from_status=(Status.UNDER_REVIEW,),
        category=Category.B,
        require_presentation_status=(PresentationStatus.COMPLETED,),
        require_funding_status=(FundingStatus.PENDING,),
        to_status=Status.APPROVED,
        required_fields=("decision_reasoning",),
        set_funding_status=FundingStatus.APPROVED,
    ),
    # Under review -> Rejected
    # Funding denied
    Transition(
        action="no_go",
        endpoint="funding-decision",
        roles=(Role.MANAGEMENT,),
        from_status=(Status.UNDER_REVIEW,),
        category=Category.B,
        require_presentation_status=(PresentationStatus.COMPLETED,),
        require_funding_status=(FundingStatus.PENDING,),
        to_status=Status.REJECTED,
        required_fields=("decision_reasoning",),
        set_funding_status=FundingStatus.DENIED,
        terminal=True,
    ),
    # Approved -> In progress
    # Work begins
    Transition(
        action="start",
        endpoint="execution",
        roles=(Role.COMMITTEE, Role.MANAGEMENT),
        from_status=(Status.APPROVED,),
        to_status=Status.IN_PROGRESS,
    ),
    # In progress -> Completed
    # Work finished
    Transition(
        action="complete",
        endpoint="execution",
        roles=(Role.COMMITTEE, Role.MANAGEMENT),
        from_status=(Status.IN_PROGRESS,),
        to_status=Status.COMPLETED,
        terminal=True,
    ),
    # === No state change ===
    # Add a comment to a request
    Transition(
        action="comment",
        endpoint="comments",
        roles=ALL_ROLES,
        from_status=NON_TERMINAL,
        required_fields=("body",),
    ),
]

# Key = action name
TRANSITIONS = {t.action: t for t in _TRANSITIONS}


def get_transition(action):
    """Return the Transition of an action
    Should return None if unknown.
    """
    return TRANSITIONS.get(action)
