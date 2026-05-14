"""
Tests d'intégration — Auth endpoints (register, login, token).
"""
import pytest
from django.contrib.auth import get_user_model
from auth_app.models.user_audit_log import UserAuditLog
from ..factories import UserFactory

User = get_user_model()

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


# ═══════════════════════════════════════════════════════════════════════
#  POST /register/
# ═══════════════════════════════════════════════════════════════════════

class TestRegisterEndpoint:

    URL = "/register/"

    def test_register_success_returns_201(self, api_client, register_payload):
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 201

    def test_register_response_contains_user_fields(self, api_client, register_payload):
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 201
        data = resp.data
        assert "id" in data
        assert data["email"] == register_payload["email"]
        assert data["username"] == register_payload["username"]
        assert data["first_name"] == register_payload["first_name"]

    def test_register_does_not_expose_password(self, api_client, register_payload):
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 201
        assert "password" not in resp.data
        assert "password_confirm" not in resp.data

    def test_register_creates_audit_log(self, api_client, register_payload):
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 201
        user = User.objects.get(email=register_payload["email"])
        assert UserAuditLog.objects.filter(user=user, action="CREATE").exists()

    def test_register_duplicate_email_returns_400(self, api_client, register_payload):
        UserFactory(email=register_payload["email"])
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 400

    def test_register_duplicate_username_returns_400(self, api_client, register_payload):
        UserFactory(username=register_payload["username"])
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 400

    def test_register_mismatched_passwords_returns_400(self, api_client, register_payload):
        register_payload["password_confirm"] = "WrongPass999!"
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 400

    def test_register_missing_email_returns_400(self, api_client, register_payload):
        del register_payload["email"]
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 400

    def test_register_short_password_returns_400(self, api_client, register_payload):
        register_payload["password"] = "short"
        register_payload["password_confirm"] = "short"
        resp = api_client.post(self.URL, register_payload, format="json")
        assert resp.status_code == 400

    def test_register_empty_body_returns_400(self, api_client):
        resp = api_client.post(self.URL, {}, format="json")
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════
#  POST /  (login)
# ═══════════════════════════════════════════════════════════════════════

class TestLoginEndpoint:

    URL = "/"

    def test_login_success_returns_200(self, api_client, user):
        resp = api_client.post(self.URL, {"email": user.email, "password": "StrongPass123!"}, format="json")
        assert resp.status_code == 200

    def test_login_returns_access_and_refresh_tokens(self, api_client, user):
        resp = api_client.post(self.URL, {"email": user.email, "password": "StrongPass123!"}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_login_wrong_password_returns_400(self, api_client, user):
        resp = api_client.post(self.URL, {"email": user.email, "password": "WrongPass!"}, format="json")
        assert resp.status_code == 400

    def test_login_unknown_email_returns_400(self, api_client):
        resp = api_client.post(self.URL, {"email": "nobody@example.com", "password": "Pass123!"}, format="json")
        assert resp.status_code == 400

    def test_login_inactive_user_returns_400(self, api_client, inactive_user):
        resp = api_client.post(
            self.URL,
            {"email": inactive_user.email, "password": "StrongPass123!"},
            format="json",
        )
        assert resp.status_code == 400

    def test_login_creates_audit_log(self, api_client, user):
        resp = api_client.post(self.URL, {"email": user.email, "password": "StrongPass123!"}, format="json")
        assert resp.status_code == 200
        assert UserAuditLog.objects.filter(user=user, action="LOGIN").exists()

    def test_login_missing_password_returns_400(self, api_client, user):
        resp = api_client.post(self.URL, {"email": user.email}, format="json")
        assert resp.status_code == 400

    def test_login_empty_body_returns_400(self, api_client):
        resp = api_client.post(self.URL, {}, format="json")
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════
#  Token refresh & verify
# ═══════════════════════════════════════════════════════════════════════

class TestTokenEndpoints:

    def _get_tokens(self, api_client, user):
        resp = api_client.post("/", {"email": user.email, "password": "StrongPass123!"}, format="json")
        return resp.data

    def test_token_refresh_returns_new_access(self, api_client, user):
        tokens = self._get_tokens(api_client, user)
        resp = api_client.post("/api/token/refresh/", {"refresh": tokens["refresh"]}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data

    def test_token_verify_valid_token_returns_200(self, api_client, user):
        tokens = self._get_tokens(api_client, user)
        resp = api_client.post("/api/token/verify/", {"token": tokens["access"]}, format="json")
        assert resp.status_code == 200