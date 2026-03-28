# tests/integration/test_admin_endpoints.py
import pytest
from auth_app.models.user_audit_log import UserAuditLog
from ..factories import UserFactory, UserProfileFactory, UserAuditLogFactory


USERS_URL = "/api/users/"
AUDIT_LOGS_URL = "/api/audit-logs/"


def toggle_url(user_id):
    return f"/api/users/{user_id}/toggle/"


@pytest.mark.integration
@pytest.mark.django_db
class TestUserListEndpoint:

    def test_admin_can_list_users(self, admin_client, db):
        UserFactory.create_batch(3)
        response = admin_client.get(USERS_URL)
        assert response.status_code == 200

    def test_non_admin_returns_403(self, auth_client):
        response = auth_client.get(USERS_URL)
        assert response.status_code == 403

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get(USERS_URL)
        assert response.status_code == 401

    def test_list_returns_all_users(self, admin_client, db):
        UserFactory.create_batch(4)
        response = admin_client.get(USERS_URL)
        assert response.data["count"] >= 4  # ← count, pas len()

    def test_list_ordered_by_created_at_desc(self, admin_client, db):
        users = UserFactory.create_batch(3)
        response = admin_client.get(USERS_URL)
        emails = [u["email"] for u in response.data["results"]]  # ← ["results"]
        assert emails.index(users[-1].email) < emails.index(users[0].email)


@pytest.mark.integration
@pytest.mark.django_db
class TestToggleUserStatusEndpoint:

    def test_admin_can_deactivate_active_user(self, admin_client, db):
        user = UserFactory(is_active=True)
        UserProfileFactory(user=user)
        response = admin_client.patch(toggle_url(user.id))
        assert response.status_code == 200
        assert response.data["is_active"] is False

    def test_admin_can_reactivate_inactive_user(self, admin_client, db):
        user = UserFactory(is_active=False)
        UserProfileFactory(user=user)
        response = admin_client.patch(toggle_url(user.id))
        assert response.status_code == 200
        assert response.data["is_active"] is True

    def test_toggle_persists_in_database(self, admin_client, db):
        user = UserFactory(is_active=True)
        admin_client.patch(toggle_url(user.id))
        user.refresh_from_db()
        assert user.is_active is False

    def test_toggle_creates_audit_log(self, admin_client, db):
        user = UserFactory()
        admin_client.patch(toggle_url(user.id))
        assert UserAuditLog.objects.filter(user=user, action="UPDATE").exists()

    def test_toggle_nonexistent_user_returns_404(self, admin_client):
        import uuid
        response = admin_client.patch(toggle_url(uuid.uuid4()))
        assert response.status_code == 404

    def test_non_admin_cannot_toggle_user(self, auth_client, db):
        user = UserFactory()
        response = auth_client.patch(toggle_url(user.id))
        assert response.status_code == 403

    def test_unauthenticated_cannot_toggle_user(self, api_client, db):
        user = UserFactory()
        response = api_client.patch(toggle_url(user.id))
        assert response.status_code == 401

    def test_toggle_response_contains_detail_and_is_active(self, admin_client, db):
        user = UserFactory(is_active=True)
        response = admin_client.patch(toggle_url(user.id))
        assert "detail" in response.data
        assert "is_active" in response.data


@pytest.mark.integration
@pytest.mark.django_db
class TestAuditLogListEndpoint:

    def test_admin_can_list_audit_logs(self, admin_client, db):
        UserAuditLogFactory.create_batch(3)
        response = admin_client.get(AUDIT_LOGS_URL)
        assert response.status_code == 200

    def test_non_admin_returns_403(self, auth_client):
        response = auth_client.get(AUDIT_LOGS_URL)
        assert response.status_code == 403

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get(AUDIT_LOGS_URL)
        assert response.status_code == 401
    
    def test_logs_count_correct(self, admin_client, db):
        UserAuditLogFactory.create_batch(5)
        response = admin_client.get(AUDIT_LOGS_URL)
        assert response.data["count"] >= 5  # ← count, pas len()

    def test_log_contains_expected_fields(self, admin_client, db):
        UserAuditLogFactory()
        response = admin_client.get(AUDIT_LOGS_URL)
        log = response.data["results"][0]  # ← ["results"][0]
        assert {"id", "user_email", "action", "ip_address", "timestamp"}.issubset(set(log.keys()))

    def test_logs_ordered_by_timestamp_desc(self, admin_client, db):
        UserAuditLogFactory.create_batch(3)
        response = admin_client.get(AUDIT_LOGS_URL)
        timestamps = [entry["timestamp"] for entry in response.data["results"]]  # ← ["results"]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_log_user_email_field_populated(self, admin_client, db):
        user = UserFactory(email="traced@example.com")
        UserAuditLogFactory(user=user, action="LOGIN")
        response = admin_client.get(AUDIT_LOGS_URL)
        emails = [entry["user_email"] for entry in response.data["results"]]  # ← ["results"]
        assert "traced@example.com" in emails