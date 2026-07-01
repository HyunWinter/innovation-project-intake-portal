"""Runs a workflow action on a request (atomic)

- Validate the action
- Update the request
- Write one AuditEvent
- Raise a TransitionError on invalid actions (400/403/404/409)
"""

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.utils import timezone

from accounts.models import Role
from proposals.models import AuditEvent, Comment

from .exceptions import (
    IllegalTransition,
    MissingFields,
    RoleNotAllowed,
    UnknownAction,
)
from .transitions import get_transition

# Realtime SSE signal (imported here to avoid circular imports)
from realtime.signals import post_transition


# Payload keys from a request
_REQUEST_FIELDS = (
    "decision_reasoning",
    "suggested_collaborators",
    "expected_resume_date",
    "presentation_requirements",
    "presentation_date",
)


@transaction.atomic
def apply_transition(request, action, actor, payload=None):
    """Run one workflow action on a request

    Parameters: request, action, actor, payload
    Returns: the updated request
    """
    payload = payload or {}

    # Look up the action, check if the actor and the request's state allow it
    transition = get_transition(action)
    if transition is None:
        raise UnknownAction(action)
    if actor.role not in transition.roles:
        raise RoleNotAllowed(action)
    if actor.role == Role.SUBMITTER and request.submitter != actor:
        raise RoleNotAllowed(action)
    _check_state(request, transition)

    # Check if an action needs payload like a decision reasoning
    missing = [f for f in transition.required_fields if not payload.get(f)]
    if missing:
        raise MissingFields(missing)

    # A comment should not change state
    if action == "comment":
        Comment.objects.create(request=request, author=actor, body=payload["body"])
        post_transition.send(
            sender=request.__class__,
            request_obj=request,
            action="comment",
            from_status=request.status,
            to_status=request.status,
            actor=actor,
        )
        return request

    from_status = request.status
    _apply_effects(request, transition, actor, payload)
    request.save()

    # One audit row per state change
    # Who did it
    # What was changed
    # From status and to status
    AuditEvent.objects.create(
        request=request,
        actor=actor,
        event_type=action,
        from_status=from_status,
        to_status=request.status,
        payload=_audit_payload(transition, payload),
    )

    # Send notification
    post_transition.send(
        sender=request.__class__,
        request_obj=request,
        action=action,
        from_status=from_status,
        to_status=request.status,
        actor=actor,
    )
    return request


def _audit_payload(t, payload):
    """For audit events
    Records the caller's input and the status changes

    Parameters: transition, payload
    Returns: a JSON-safe dict
    """
    data = dict(payload)
    if t.set_committee_decision is not None:
        data["committee_decision"] = t.set_committee_decision
    if t.set_presentation_status is not None:
        data["presentation_status"] = t.set_presentation_status
    if t.set_funding_status is not None:
        data["funding_status"] = t.set_funding_status

    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def _check_state(request, t):
    """Check state of a request
    If the request isn't in the right state transition,
    Reject the action

    Parameters: request, transition
    Returns: Raises IllegalTransition
    """
    if request.status not in t.from_status:
        raise IllegalTransition(f"'{t.action}' not allowed from '{request.status}'")
    if t.category is not None and request.category != t.category:
        raise IllegalTransition(f"'{t.action}' not allowed from category '{request.category}'")
    if (
        t.require_presentation_status is not None
        and request.presentation_status not in t.require_presentation_status
    ):
        raise IllegalTransition(f"'{t.action}' needs a different presentation status")
    if (
        t.require_funding_status is not None
        and request.funding_status not in t.require_funding_status
    ):
        raise IllegalTransition(f"'{t.action}' needs a different funding status")


def _apply_effects(request, t, actor, payload):
    """Apply status changes and the payload fields to the request

    Parameters: request, transition, actor, payload
    Returns: nothing
    """
    if t.to_status is not None:
        request.status = t.to_status
    if t.set_committee_decision is not None:
        request.committee_decision = t.set_committee_decision
    if t.set_presentation_status is not None:
        request.presentation_status = t.set_presentation_status
    if t.set_funding_status is not None:
        request.funding_status = t.set_funding_status

    for field in _REQUEST_FIELDS:
        if field in payload:
            setattr(request, field, payload[field])

    # Who and when for reasoning
    if "decision_reasoning" in t.required_fields:
        request.decision_made_by = actor
        request.decision_made_at = timezone.now()
