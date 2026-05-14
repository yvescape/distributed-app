"""
Tests d'intégration — Admin endpoints (user list, toggle status, audit logs).
"""
import pytest
from django.contrib.auth import get_user_model
from auth_app.models.user_audit_log import UserAuditLog
from ..factories import UserFactory, UserAuditLogFactory

User = get_user_model()

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


# ═══════════════════════════════════════════════════════════════════════
#  GET /list/
# ═══════════════════════════════════════════════════════════════════════

class TestUserListEndpoint:

    URL = "/list/"

    def test_admin_can_list_users(self, admin_client):
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200

    def test_non_admin_returns_403(self, auth_client):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 401

    def test_list_returns_all_users(self, admin_client, admin_user):
        UserFactory.create_batch(3)
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200
        # admin_user + 3 créés = 4
        assert len(resp.data) == 4

    def test_list_ordered_by_created_at_desc(self, admin_client, admin_user):
        UserFactory.create_batch(2)
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200
        results = resp.data["results"] if "results" in resp.data else resp.data
        dates = [item["created_at"] for item in results]
        assert dates == sorted(dates, reverse=True)

# ═══════════════════════════════════════════════════════════════════════
#  PATCH /<user_id>/toggle/
# ═══════════════════════════════════════════════════════════════════════

class TestToggleUserStatusEndpoint:

    def _url(self, user_id):
        return f"/{user_id}/toggle/"

    def test_admin_can_deactivate_active_user(self, admin_client, user):
        assert user.is_active is True
        resp = admin_client.patch(self._url(user.id))
        assert resp.status_code == 200
        assert resp.data["is_active"] is False

    def test_admin_can_reactivate_inactive_user(self, admin_client, inactive_user):
        resp = admin_client.patch(self._url(inactive_user.id))
        assert resp.status_code == 200
        assert resp.data["is_active"] is True

    def test_toggle_persists_in_database(self, admin_client, user):
        admin_client.patch(self._url(user.id))
        user.refresh_from_db()
        assert user.is_active is False

    def test_toggle_creates_audit_log(self, admin_client, user):
        admin_client.patch(self._url(user.id))
        assert UserAuditLog.objects.filter(user=user, action="UPDATE").exists()

    def test_non_admin_cannot_toggle_user(self, auth_client, user):
        other_user = UserFactory()
        resp = auth_client.patch(self._url(other_user.id))
        assert resp.status_code == 403

    def test_unauthenticated_cannot_toggle_user(self, api_client, user):
        resp = api_client.patch(self._url(user.id))
        assert resp.status_code == 401

    def test_toggle_response_contains_detail_and_is_active(self, admin_client, user):
        resp = admin_client.patch(self._url(user.id))
        assert resp.status_code == 200
        assert "detail" in resp.data
        assert "is_active" in resp.data


# ═══════════════════════════════════════════════════════════════════════
#  GET /audit-logs/
# ═══════════════════════════════════════════════════════════════════════

class TestAuditLogListEndpoint:

    URL = "/audit-logs/"

    def _get_results(self, resp):
        """Extraire la liste, paginée ou non."""
        return resp.data["results"] if "results" in resp.data else resp.data

    def test_admin_can_list_audit_logs(self, admin_client):
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200

    def test_non_admin_returns_403(self, auth_client):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 403

    def test_unauthenticated_returns_401(self, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 401

    def test_logs_count_correct(self, admin_client):
        UserAuditLogFactory.create_batch(5)
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200
        results = self._get_results(resp)
        assert len(results) == 5

    def test_log_contains_expected_fields(self, admin_client):
        UserAuditLogFactory()
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200
        results = self._get_results(resp)
        log = results[0]
        expected = {"id", "user_email", "action", "ip_address", "timestamp"}
        assert set(log.keys()) == expected

    def test_logs_ordered_by_timestamp_desc(self, admin_client):
        UserAuditLogFactory.create_batch(3)
        resp = admin_client.get(self.URL)
        results = self._get_results(resp)
        timestamps = [item["timestamp"] for item in results]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_log_user_email_field_populated(self, admin_client):
        log = UserAuditLogFactory()
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200
        results = self._get_results(resp)
        assert results[0]["user_email"] == log.user.email