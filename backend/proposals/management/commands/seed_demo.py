from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Role
from proposals.enums import (
    Category,
    CommitteeDecision,
    FundingStatus,
    PresentationStatus,
    Status,
    TechCategory,
)
from proposals.models import Request

User = get_user_model()

DEMO_PASSWORD = "demo1234"
DEMO_USERS = [
    ("submitter@example.com", "Andrew Submitter", Role.SUBMITTER),
    ("committee@example.com", "Ben Committee", Role.COMMITTEE),
    ("management@example.com", "Colin Management", Role.MANAGEMENT),
]


class Command(BaseCommand):
    """Seed the database with demo users and sample requests
    Requirement:
    - demo users
    - 1 pending Cat-A
    - 1 pending Cat-B
    - 1 Cat-B mid-flow (awaiting funding)
    - 1 completed
    - 1 rejected

    Command:
    cd backend
    docker compose exec backend python manage.py seed_demo
    """

    help = "Create three demo users and the five sample requests"

    @transaction.atomic
    def handle(self, *args, **options):
        users = {role: self._user(email, name, role) for email, name, role in DEMO_USERS}
        submitter = users[Role.SUBMITTER]
        committee = users[Role.COMMITTEE]

        # Drop previously seeded requests by the demo submitter.
        Request.all_objects.filter(submitter=submitter).delete()

        self._category_a_pending(submitter)
        self._category_b_pending(submitter)
        self._category_b_awaiting_funding(submitter, committee)
        self._completed(submitter, committee)
        self._rejected(submitter, committee)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(DEMO_USERS)} users (password '{DEMO_PASSWORD}') and 5 requests."
            )
        )

    def _user(self, email, name, role):
        user = User.objects.filter(email=email).first()
        if user is None:
            return User.objects.create_user(
                email=email, name=name, role=role, password=DEMO_PASSWORD
            )
        user.name, user.role = name, role
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user

    def _base(self, submitter, **overrides):
        data = {
            "submitter": submitter,
            "contact_name": submitter.name,
            "contact_email": submitter.email,
            "tech_category": TechCategory.OTHER,
            "title": "Untitled",
            "description": "Demo description.",
            "objectives": "Demo objectives.",
        }
        data.update(overrides)
        return Request.objects.create(**data)

    def _category_a_pending(self, submitter):
        return self._base(
            submitter,
            title="Internal project checklist app (Category A, Pending)",
            category=Category.A,
            status=Status.PENDING,
            funding_required=False,
            funding_status=FundingStatus.NOT_REQUIRED,
        )

    def _category_b_pending(self, submitter):
        return self._base(
            submitter,
            title="Maintenance prediction AI app (Category B, Pending)",
            category=Category.B,
            status=Status.PENDING,
            funding_required=True,
            funding_status=FundingStatus.PENDING,
            budget=50000,
            estimated_roi="Could save ~100 maintenance hours per quarter",
        )

    def _category_b_awaiting_funding(self, submitter, committee):
        return self._base(
            submitter,
            title="Vision QA line scanner (Category B, Funding Awaiting)",
            category=Category.B,
            status=Status.UNDER_REVIEW,
            funding_required=True,
            funding_status=FundingStatus.PENDING,
            presentation_status=PresentationStatus.COMPLETED,
            committee_decision=CommitteeDecision.REQUEST_PRESENTATION,
            decision_reasoning="This actually sounds promising! I asked them to present.",
            decision_made_by=committee,
            decision_made_at=timezone.now(),
            presentation_date=timezone.now(),
            budget=120000,
            estimated_roi="Could cut defect escapes by ~30%.",
        )

    def _completed(self, submitter, committee):
        return self._base(
            submitter,
            title="Internal documentation search bot (Category A, Completed)",
            category=Category.A,
            status=Status.COMPLETED,
            funding_required=False,
            funding_status=FundingStatus.NOT_REQUIRED,
            committee_decision=CommitteeDecision.PROCEED_INDEPENDENTLY,
            decision_reasoning="Clear standalone win.",
            decision_made_by=committee,
            decision_made_at=timezone.now(),
        )

    def _rejected(self, submitter, committee):
        return self._base(
            submitter,
            title="Self-hosted team chat tool (Category A, Rejected)",
            category=Category.A,
            status=Status.REJECTED,
            funding_required=False,
            funding_status=FundingStatus.NOT_REQUIRED,
            committee_decision=CommitteeDecision.REJECT,
            decision_reasoning="We already use Slack. No reason to build our own.",
            decision_made_by=committee,
            decision_made_at=timezone.now(),
        )
