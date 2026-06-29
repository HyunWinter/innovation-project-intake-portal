"""Shared builders for the proposals test suite."""

from accounts.models import Role, User


def make_users():
    """One user per role, keyed by role."""
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
