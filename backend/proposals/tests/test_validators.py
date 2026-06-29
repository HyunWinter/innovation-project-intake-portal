"""Unit tests for input validation
- Create serializer
- Payload checks
"""

from datetime import timedelta
from types import SimpleNamespace

from django.test import TestCase
from django.utils import timezone
from rest_framework.serializers import ValidationError

from accounts.models import Role
from proposals.enums import Category, FundingStatus, Status
from proposals.serializers import RequestCreateSerializer
from proposals.validators import validate_transition_payload

from .helpers import make_users


class RequestValidationTests(TestCase):
    """RequestCreateSerializer
    Field validation and category derivation
    """

    @classmethod
    def setUpTestData(cls):
        users = make_users()
        cls.submitter = users[Role.SUBMITTER]

    def base_payload(self, **overrides):
        data = dict(
            contact_name="Submitter",
            contact_email="submitter@example.com",
            title="Title",
            description="Description",
            objectives="Objectives",
            funding_required=False,
        )
        data.update(overrides)
        return data

    def test_end_before_start_rejected(self):
        # Tests: end_date before start_date
        # Expects: invalid, end_date error
        s = RequestCreateSerializer(
            data=self.base_payload(start_date="2026-02-01", end_date="2026-01-01")
        )
        self.assertFalse(s.is_valid())
        self.assertIn("end_date", s.errors)

    def test_funded_requires_budget(self):
        # Tests: funded request with no budget
        # Expects: invalid, budget error
        s = RequestCreateSerializer(
            data=self.base_payload(funding_required=True, estimated_roi="x")
        )
        self.assertFalse(s.is_valid())
        self.assertIn("budget", s.errors)

    def test_funded_budget_must_be_positive(self):
        # Tests: funded request with budget 0
        # Expects: invalid, budget error
        s = RequestCreateSerializer(
            data=self.base_payload(funding_required=True, budget=0, estimated_roi="estimated roi")
        )
        self.assertFalse(s.is_valid())
        self.assertIn("budget", s.errors)

    def test_funded_requires_roi(self):
        # Tests: funded request with no ROI
        # Expects: invalid, estimated_roi error
        s = RequestCreateSerializer(data=self.base_payload(funding_required=True, budget=1000))
        self.assertFalse(s.is_valid())
        self.assertIn("estimated_roi", s.errors)

    def test_unfunded_minimal_is_valid(self):
        # Tests: minimal unfunded request
        # Expects: valid
        s = RequestCreateSerializer(data=self.base_payload())
        self.assertTrue(s.is_valid(), s.errors)

    def test_create_derives_category_a(self):
        # Tests: create with funding off
        # Expects: Category A, funding not required, pending
        ctx = {"request": SimpleNamespace(user=self.submitter)}
        s = RequestCreateSerializer(data=self.base_payload(), context=ctx)
        self.assertTrue(s.is_valid(), s.errors)
        obj = s.save()
        self.assertEqual(obj.category, Category.A)
        self.assertEqual(obj.funding_status, FundingStatus.NOT_REQUIRED)
        self.assertEqual(obj.status, Status.PENDING)
        self.assertEqual(obj.submitter, self.submitter)

    def test_create_derives_category_b(self):
        # Tests: create with funding on
        # Expects: Category B, funding pending
        ctx = {"request": SimpleNamespace(user=self.submitter)}
        s = RequestCreateSerializer(
            data=self.base_payload(funding_required=True, budget=1000, estimated_roi="saves time"),
            context=ctx,
        )
        self.assertTrue(s.is_valid(), s.errors)
        obj = s.save()
        self.assertEqual(obj.category, Category.B)
        self.assertEqual(obj.funding_status, FundingStatus.PENDING)


class TransitionPayloadTests(TestCase):
    """validate_transition_payload: typed checks the registry can't express."""

    def test_schedule_past_date_rejected(self):
        # Tests: schedule with a past date
        # Expects: ValidationError
        with self.assertRaises(ValidationError):
            validate_transition_payload(
                "schedule", {"presentation_date": (timezone.now() - timedelta(days=1)).isoformat()}
            )

    def test_schedule_future_date_ok(self):
        # Tests: schedule with a future date
        # Expects: passes
        validate_transition_payload(
            "schedule", {"presentation_date": (timezone.now() + timedelta(days=1)).isoformat()}
        )

    def test_schedule_missing_date_passes(self):
        # Tests: schedule with no date
        # Expects: passes (absence is the service's MissingFields case)
        validate_transition_payload("schedule", {})

    def test_hold_malformed_date_rejected(self):
        # Tests: hold with a malformed date
        # Expects: ValidationError
        with self.assertRaises(ValidationError):
            validate_transition_payload("hold", {"expected_resume_date": "not-a-date"})

    def test_hold_valid_date_ok(self):
        # Tests: hold with a valid date
        # Expects: passes
        validate_transition_payload("hold", {"expected_resume_date": "2099-01-01"})

    def test_action_without_typed_checks_ok(self):
        # Tests: an action with no typed checks
        # Expects: passes
        validate_transition_payload("reject", {"decision_reasoning": "x"})
