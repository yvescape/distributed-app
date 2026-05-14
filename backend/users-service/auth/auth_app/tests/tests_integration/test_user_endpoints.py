"""
Tests d'intégration — User endpoints (me, update).
"""
import pytest
from django.contrib.auth import get_user_model
from auth_app.models.user_audit_log import UserAuditLog

User = get_user_model()

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


# ═══════════════════════════════════════════════════════════════════════
#  GET /me/
# ═══════════════════════════════════════════════════════════════════════

class TestMeEndpoint:

    URL = "/me/"

    def test_me_authenticated_returns_200(self, auth_client):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200

    def test_me_returns_own_user_data(self, auth_client, user):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        assert resp.data["email"] == user.email
        assert resp.data["username"] == user.username

    def test_me_unauthenticated_returns_401(self, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 401

    def test_me_does_not_expose_password(self, auth_client):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        assert "password" not in resp.data

    def test_me_contains_expected_fields(self, auth_client):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        expected = {
            "id", "email", "username", "first_name", "last_name",
            "is_active", "is_email_verified", "created_at",
        }
        assert set(resp.data.keys()) == expected


# ═══════════════════════════════════════════════════════════════════════
#  PATCH /update/
# ═══════════════════════════════════════════════════════════════════════

class TestUpdateUserEndpoint:

    URL = "/update/"

    def test_update_first_name_returns_200(self, auth_client):
        resp = auth_client.patch(self.URL, {"first_name": "NewFirst"}, format="json")
        assert resp.status_code == 200

    def test_update_persists_new_first_name(self, auth_client, user):
        auth_client.patch(self.URL, {"first_name": "NewFirst"}, format="json")
        user.refresh_from_db()
        assert user.first_name == "NewFirst"

    def test_update_creates_audit_log(self, auth_client, user):
        auth_client.patch(self.URL, {"first_name": "Changed"}, format="json")
        assert UserAuditLog.objects.filter(user=user, action="UPDATE").exists()

    def test_update_unauthenticated_returns_401(self, api_client):
        resp = api_client.patch(self.URL, {"first_name": "Nope"}, format="json")
        assert resp.status_code == 401