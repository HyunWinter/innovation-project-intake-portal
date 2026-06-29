"""Integration tests (HTTP)
- Endpoints
- Role gating
- Error contract
"""

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import Role, User
from proposals.enums import Category, FundingStatus

from .helpers import build_request, make_users


class APIIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = make_users()
        cls.submitter = users[Role.SUBMITTER]
        cls.committee = users[Role.COMMITTEE]
        cls.management = users[Role.MANAGEMENT]

    def setUp(self):
        self.client = APIClient()

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_list_requires_authentication(self):
        # Tests: list without auth
        # Expects: 401
        self.assertEqual(self.client.get("/api/requests/").status_code, 401)

    def test_submitter_creates_category_a(self):
        # Tests: submitter creates an unfunded request
        # Expects: 201, Category A, create audit row
        self.auth(self.submitter)
        resp = self.client.post(
            "/api/requests/",
            {
                "title": "title",
                "description": "description",
                "objectives": "objectives",
                "contact_name": "A",
                "contact_email": "submitter@example.com",
                "funding_required": False,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["category"], "A")
        self.assertTrue(any(e["event_type"] == "create" for e in resp.data["audit_events"]))

    def test_non_submitter_cannot_create(self):
        # Tests: committee tries to create
        # Expects: 403
        self.auth(self.committee)
        resp = self.client.post(
            "/api/requests/",
            {
                "title": "title",
                "description": "description",
                "objectives": "objectives",
                "contact_name": "A",
                "contact_email": "submitter@example.com",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_create_validation_error(self):
        # Tests: funded create missing budget/ROI
        # Expects: 400
        self.auth(self.submitter)
        resp = self.client.post(
            "/api/requests/",
            {
                "title": "title",
                "description": "description",
                "objectives": "objectives",
                "contact_name": "A",
                "contact_email": "submitter@example.com",
                "funding_required": True,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_list_filter_by_category(self):
        # Tests: list filtered by category=B
        # Expects: only Cat-B rows
        build_request(self.submitter, title="A one")
        build_request(
            self.submitter,
            category=Category.B,
            funding_required=True,
            funding_status=FundingStatus.PENDING,
            budget=10,
            title="B one",
        )
        self.auth(self.committee)
        resp = self.client.get("/api/requests/?category=B")
        self.assertEqual(resp.status_code, 200)
        titles = [r["title"] for r in resp.data["results"]]
        self.assertIn("B one", titles)
        self.assertNotIn("A one", titles)

    def test_detail_has_engine_fields(self):
        # Tests: fetch request detail
        # Expects: available_actions, workflow, audit_events present
        req = build_request(self.submitter)
        self.auth(self.committee)
        resp = self.client.get(f"/api/requests/{req.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("workflow", resp.data)
        self.assertIn("audit_events", resp.data)
        self.assertIn("proceed_independently", resp.data["available_actions"])

    def test_committee_decision_via_api(self):
        # Tests: committee decision over HTTP
        # Expects: 200, status approved
        req = build_request(self.submitter)
        self.auth(self.committee)
        resp = self.client.post(
            f"/api/requests/{req.id}/committee-decision/",
            {"action": "proceed_independently", "decision_reasoning": "ok"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "approved")

    def test_comment_via_api(self):
        # Tests: post a comment
        # Expects: 200, comment listed
        req = build_request(self.submitter)
        self.auth(self.submitter)
        resp = self.client.post(
            f"/api/requests/{req.id}/comments/",
            {"action": "comment", "body": "hi"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["comments"]), 1)

    def test_resubmit_owner_while_pending(self):
        # Tests: owner resubmits a pending request
        # Expects: 200, fields updated
        req = build_request(self.submitter, title="old")
        self.auth(self.submitter)
        resp = self.client.patch(f"/api/requests/{req.id}/", {"title": "new"}, format="json")
        self.assertEqual(resp.status_code, 200)
        req.refresh_from_db()
        self.assertEqual(req.title, "new")

    def test_resubmit_non_owner_forbidden(self):
        # Tests: non-owner resubmits
        # Expects: 403
        other = User.objects.create_user("another.submitter@example.com", "O", Role.SUBMITTER, "pw")
        req = build_request(self.submitter)
        self.auth(other)
        resp = self.client.patch(f"/api/requests/{req.id}/", {"title": "title"}, format="json")
        self.assertEqual(resp.status_code, 403)

    # --- error contract ---

    def test_409_illegal_transition(self):
        # Tests: funding a Cat-A request over HTTP
        # Expects: 409
        req = build_request(self.submitter)
        self.auth(self.management)
        resp = self.client.post(
            f"/api/requests/{req.id}/funding-decision/",
            {"action": "go", "decision_reasoning": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_403_wrong_role(self):
        # Tests: submitter runs a committee action
        # Expects: 403
        req = build_request(self.submitter)
        self.auth(self.submitter)
        resp = self.client.post(
            f"/api/requests/{req.id}/committee-decision/",
            {"action": "reject", "decision_reasoning": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_404_unknown_action(self):
        # Tests: an unknown action
        # Expects: 404
        req = build_request(self.submitter)
        self.auth(self.committee)
        resp = self.client.post(
            f"/api/requests/{req.id}/committee-decision/",
            {"action": "bogus", "decision_reasoning": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_400_missing_field(self):
        # Tests: decision missing its required field
        # Expects: 400 with the field listed
        req = build_request(self.submitter)
        self.auth(self.committee)
        resp = self.client.post(
            f"/api/requests/{req.id}/committee-decision/",
            {"action": "reject"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("decision_reasoning", resp.data.get("fields", []))
