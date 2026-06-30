"""Read only helpers over the transition registry"""

from proposals.enums import Category, Status
from .transitions import TRANSITIONS


def available_actions(request, role):
    """Find which actions a role can run on a request

    Parameters: request, role
    Returns: list of dicts (for the frontend buttons and modals from data)
        action          - the action name ("proceed_independently")
        endpoint        - URL segment to POST to ("committee-decision")
        required_fields - the action's payload
    """
    actions = []
    for t in TRANSITIONS.values():
        if role not in t.roles:
            continue
        if request.status not in t.from_status:
            continue
        if t.category is not None and request.category != t.category:
            continue
        if (
            t.require_presentation_status is not None
            and request.presentation_status not in t.require_presentation_status
        ):
            continue
        if (
            t.require_funding_status is not None
            and request.funding_status not in t.require_funding_status
        ):
            continue
        actions.append(
            {
                "action": t.action,
                "endpoint": t.endpoint,
                "required_fields": list(t.required_fields),
            }
        )
    return actions


def _status_order(category):
    """The statuses shown in the review screen -> progress component

    Parameters: category
    Returns: list of Status values
    """
    if category == Category.B:
        return [
            Status.PENDING,
            Status.UNDER_REVIEW,
            Status.APPROVED,
            Status.IN_PROGRESS,
            Status.COMPLETED,
        ]
    return [Status.PENDING, Status.APPROVED, Status.IN_PROGRESS, Status.COMPLETED]


def workflow_status(request):
    """Progress shown in the review screen

    Parameters: request
    Returns: statuses
        status  - under_review
        label   - Under review
        state   - complete, current, or pending
    """
    order = _status_order(request.category)

    # on_hold = pending stage
    # if not, return the actual status
    current = Status.PENDING if request.status == Status.ON_HOLD else request.status
    pos = order.index(current) if current in order else None

    result = []
    for i, status in enumerate(order):
        if request.status == Status.COMPLETED or (pos is not None and i < pos):
            state = "complete"
        elif pos is not None and i == pos:
            state = "current"
        else:
            state = "pending"
        result.append({"status": status.value, "label": status.label, "state": state})
    return result
