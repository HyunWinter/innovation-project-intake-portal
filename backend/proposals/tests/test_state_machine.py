"""Unit tests for apply_transition
- Effects for testing successful transitions
- Guards for testing rejected transitions
"""

from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import Role
from proposals.enums import (
    Category,
    CommitteeDecision,
    FundingStatus,
    PresentationStatus,
    Status,
)
from workflow.exceptions import (
    IllegalTransition,
    MissingFields,
    RoleNotAllowed,
    UnknownAction,
)
from workflow.service import apply_transition

from .helpers import build_request, make_users


class StateMachineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = make_users()
        cls.submitter = users[Role.SUBMITTER]
        cls.committee = users[Role.COMMITTEE]
        cls.management = users[Role.MANAGEMENT]

    def make_cat_b(self, **overrides):
        return build_request(
            self.submitter,
            category=Category.B,
            funding_required=True,
            funding_status=FundingStatus.PENDING,
            budget=1000,
            **overrides,
        )

    """Effects (successful transition tests)"""

    def test_proceed_independently_approves_and_audits(self):
        # Tests: committee proceeds on a Category A request
        # Expects: approved, decision recorded, one audit row
        req = build_request(self.submitter)
        apply_transition(req, "proceed_independently", self.committee, {"decision_reasoning": "ok"})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.APPROVED)
        self.assertEqual(req.committee_decision, CommitteeDecision.PROCEED_INDEPENDENTLY)
        self.assertEqual(req.decision_made_by, self.committee)
        self.assertIsNotNone(req.decision_made_at)
        ev = req.audit_events.get()
        self.assertEqual(
            (ev.from_status, ev.to_status, ev.actor),
            (Status.PENDING, Status.APPROVED, self.committee),
        )
        self.assertEqual(ev.event_type, "proceed_independently")

    def test_category_a_full_path_to_completed(self):
        # Tests: Category A approve -> start -> complete
        # Expects: status ends at completed
        req = build_request(self.submitter)
        apply_transition(req, "proceed_independently", self.committee, {"decision_reasoning": "ok"})
        apply_transition(req, "start", self.committee, {})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.IN_PROGRESS)
        apply_transition(req, "complete", self.committee, {})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.COMPLETED)

    def test_category_b_full_path_to_approved(self):
        # Tests: Category B request_presentation -> schedule -> advance -> fund
        # Expects: approved, funding approved
        req = self.make_cat_b()
        apply_transition(
            req,
            "request_presentation",
            self.committee,
            {"decision_reasoning": "present", "presentation_requirements": "slides"},
        )
        req.refresh_from_db()
        self.assertEqual(req.status, Status.UNDER_REVIEW)
        self.assertEqual(req.presentation_status, PresentationStatus.REQUESTED)

        apply_transition(
            req,
            "schedule",
            self.committee,
            {"presentation_date": timezone.now() + timedelta(days=3)},
        )
        req.refresh_from_db()
        self.assertEqual(req.presentation_status, PresentationStatus.SCHEDULED)

        apply_transition(req, "advanced", self.committee, {})
        req.refresh_from_db()
        self.assertEqual(req.presentation_status, PresentationStatus.COMPLETED)

        apply_transition(req, "go", self.management, {"decision_reasoning": "fund it"})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.APPROVED)
        self.assertEqual(req.funding_status, FundingStatus.APPROVED)

    def test_hold_then_resume(self):
        # Tests: hold a request, then resume it
        # Expects: on_hold, then back to pending
        req = build_request(self.submitter)
        apply_transition(
            req,
            "hold",
            self.committee,
            {"decision_reasoning": "wait", "expected_resume_date": date.today()},
        )
        req.refresh_from_db()
        self.assertEqual(req.status, Status.ON_HOLD)
        apply_transition(req, "resume", self.committee, {})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.PENDING)

    def test_comment_does_not_change_state(self):
        # Tests: add a comment
        # Expects: state unchanged, comment saved, no audit row
        req = build_request(self.submitter)
        apply_transition(req, "comment", self.submitter, {"body": "hello"})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.PENDING)
        self.assertEqual(req.comments.count(), 1)
        self.assertEqual(req.audit_events.count(), 0)

    """Guards (illegal transitions + role/field checks)"""

    def test_funding_on_category_a_rejected(self):
        # Tests: funding action on a Category A request
        # Expects: IllegalTransition, nothing written
        req = build_request(self.submitter)
        with self.assertRaises(IllegalTransition):
            apply_transition(req, "go", self.management, {"decision_reasoning": "x"})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.PENDING)
        self.assertEqual(req.audit_events.count(), 0)

    def test_presentation_outcome_before_scheduled_rejected(self):
        # Tests: record outcome while status is requested, not scheduled
        # Expects: IllegalTransition
        req = self.make_cat_b()
        apply_transition(
            req,
            "request_presentation",
            self.committee,
            {"decision_reasoning": "r", "presentation_requirements": "req"},
        )
        with self.assertRaises(IllegalTransition):
            apply_transition(req, "advanced", self.committee, {})

    def test_no_action_after_terminal(self):
        # Tests: act on a rejected (terminal) request
        # Expects: IllegalTransition
        req = build_request(self.submitter)
        apply_transition(req, "reject", self.committee, {"decision_reasoning": "no"})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.REJECTED)
        with self.assertRaises(IllegalTransition):
            apply_transition(req, "start", self.committee, {})

    def test_wrong_role_rejected(self):
        # Tests: submitter runs a committee only action
        # Expects: RoleNotAllowed, nothing written
        req = build_request(self.submitter)
        with self.assertRaises(RoleNotAllowed):
            apply_transition(
                req, "proceed_independently", self.submitter, {"decision_reasoning": "x"}
            )
        req.refresh_from_db()
        self.assertEqual(req.audit_events.count(), 0)

    def test_missing_required_field_rejected(self):
        # Tests: decision without its required field
        # Expects: MissingFields, nothing written
        req = build_request(self.submitter)
        with self.assertRaises(MissingFields):
            apply_transition(req, "proceed_independently", self.committee, {})
        req.refresh_from_db()
        self.assertEqual(req.status, Status.PENDING)
        self.assertEqual(req.audit_events.count(), 0)

    def test_unknown_action_rejected(self):
        # Tests: an unregistered action
        # Expects: UnknownAction
        req = build_request(self.submitter)
        with self.assertRaises(UnknownAction):
            apply_transition(req, "definitely_not_real", self.committee, {})
