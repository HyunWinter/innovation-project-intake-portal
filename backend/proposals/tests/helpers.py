"""Shared builders for the proposals test suite."""

from accounts.models import Role, User
from proposals.enums import Category, FundingStatus, Status
from proposals.models import Request


def make_users():
    """Three users (email, password, role) keyed by roles"""
    return {
        Role.SUBMITTER: User.objects.create_user(
            "submitter@example.com", "Submitter", Role.SUBMITTER, "extremelysecurepassword1"
        ),
        Role.COMMITTEE: User.objects.create_user(
            "committeee@example.com", "Committeee", Role.COMMITTEE, "extremelysecurepassword2"
        ),
        Role.MANAGEMENT: User.objects.create_user(
            "management@example.com", "Management", Role.MANAGEMENT, "extremelysecurepassword3"
        ),
    }


def build_request(submitter, **overrides):
    """A Category A pending request for state machine and api tests"""
    data = dict(
        category=Category.A,
        status=Status.PENDING,
        submitter=submitter,
        contact_name="Submitter",
        contact_email="submitter@example.com",
        title="Title",
        description="Description",
        objectives="Objectives",
        funding_required=False,
        funding_status=FundingStatus.NOT_REQUIRED,
    )
    data.update(overrides)
    return Request.objects.create(**data)
