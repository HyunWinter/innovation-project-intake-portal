"""Authentication tests
- JWT login
- The role claim
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import Role, User


class AuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            "superdupervaliduser@example.com", "Auth", Role.COMMITTEE, "verysecretpassword"
        )

    def setUp(self):
        self.client = APIClient()

    def test_token_carries_role_and_name_claims(self):
        # Tests: log in with valid credentials
        # Expects: 200, token with role/name
        resp = self.client.post(
            "/api/token/",
            {"email": "superdupervaliduser@example.com", "password": "verysecretpassword"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        token = AccessToken(resp.data["access"])
        self.assertEqual(token["role"], Role.COMMITTEE)
        self.assertEqual(token["name"], "Auth")

    def test_wrong_password_rejected(self):
        # Tests: log in with wrong password
        # Expects: 401
        resp = self.client.post(
            "/api/token/",
            {"email": "superdupervaliduser@example.com", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_protected_endpoint_requires_auth(self):
        # Tests: hit a protected endpoint with no token
        # Expects: 401
        resp = self.client.get("/api/requests/")
        self.assertEqual(resp.status_code, 401)
