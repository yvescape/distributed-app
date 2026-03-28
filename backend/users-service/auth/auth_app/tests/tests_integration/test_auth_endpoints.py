# tests/integration/test_auth_endpoints.py
import pytest
from auth_app.models.user_audit_log import UserAuditLog
from auth_app.models.user_profile import UserProfile
from ..factories import UserFactory, UserProfileFactory


REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
TOKEN_REFRESH_URL = "/api/token/refresh/"
TOKEN_VERIFY_URL = "/api/token/verify/"


@pytest.mark.integration
@pytest.mark.django_db
class TestRegisterEndpoint:

    def test_register_success_returns_201(self, api_client, register_payload):
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        assert response.status_code == 201

    def test_register_response_contains_user_fields(self, api_client, register_payload):
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        data = response.data
        assert data["email"] == register_payload["email"]
        assert data["username"] == register_payload["username"]
        assert "id" in data

    def test_register_does_not_expose_password(self, api_client, register_payload):
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        assert "password" not in response.data
        assert "password_confirm" not in response.data

    def test_register_creates_profile_automatically(self, api_client, register_payload):
        api_client.post(REGISTER_URL, data=register_payload, format="json")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email=register_payload["email"])
        assert UserProfile.objects.filter(user=user).exists()

    def test_register_creates_audit_log(self, api_client, register_payload):
        api_client.post(REGISTER_URL, data=register_payload, format="json")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email=register_payload["email"])
        assert UserAuditLog.objects.filter(user=user, action="CREATE").exists()

    def test_register_duplicate_email_returns_400(self, api_client, register_payload, db):
        UserFactory(email=register_payload["email"])
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        assert response.status_code == 400
        assert "email" in response.data

    def test_register_duplicate_username_returns_400(self, api_client, register_payload, db):
        UserFactory(username=register_payload["username"])
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        assert response.status_code == 400
        assert "username" in response.data

    def test_register_mismatched_passwords_returns_400(self, api_client, register_payload):
        register_payload["password_confirm"] = "DifferentPass!"
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        assert response.status_code == 400

    def test_register_missing_email_returns_400(self, api_client, register_payload):
        del register_payload["email"]
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        assert response.status_code == 400
        assert "email" in response.data

    def test_register_short_password_returns_400(self, api_client, register_payload):
        register_payload["password"] = "123"
        register_payload["password_confirm"] = "123"
        response = api_client.post(REGISTER_URL, data=register_payload, format="json")
        assert response.status_code == 400

    def test_register_empty_body_returns_400(self, api_client):
        response = api_client.post(REGISTER_URL, data={}, format="json")
        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.django_db
class TestLoginEndpoint:

    def test_login_success_returns_200(self, api_client, user):
        response = api_client.post(LOGIN_URL, data={"email": user.email, "password": "StrongPass123!"}, format="json")
        assert response.status_code == 200

    def test_login_returns_access_and_refresh_tokens(self, api_client, user):
        response = api_client.post(LOGIN_URL, data={"email": user.email, "password": "StrongPass123!"}, format="json")
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password_returns_400(self, api_client, user):
        response = api_client.post(LOGIN_URL, data={"email": user.email, "password": "WrongPassword!"}, format="json")
        assert response.status_code == 400

    def test_login_unknown_email_returns_400(self, api_client):
        response = api_client.post(LOGIN_URL, data={"email": "ghost@example.com", "password": "Pass123!"}, format="json")
        assert response.status_code == 400

    def test_login_inactive_user_returns_400(self, api_client, inactive_user):
        response = api_client.post(LOGIN_URL, data={"email": inactive_user.email, "password": "StrongPass123!"}, format="json")
        assert response.status_code == 400
        assert "désactivé" in str(response.data)

    def test_login_creates_audit_log(self, api_client, user):
        api_client.post(LOGIN_URL, data={"email": user.email, "password": "StrongPass123!"}, format="json")
        assert UserAuditLog.objects.filter(user=user, action="LOGIN").exists()

    def test_login_missing_password_returns_400(self, api_client, user):
        response = api_client.post(LOGIN_URL, data={"email": user.email}, format="json")
        assert response.status_code == 400

    def test_login_empty_body_returns_400(self, api_client):
        response = api_client.post(LOGIN_URL, data={}, format="json")
        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.django_db
class TestTokenEndpoints:

    def _get_tokens(self, api_client, user):
        response = api_client.post(LOGIN_URL, data={"email": user.email, "password": "StrongPass123!"}, format="json")
        return response.data

    def test_token_refresh_returns_new_access(self, api_client, user):
        tokens = self._get_tokens(api_client, user)
        response = api_client.post(TOKEN_REFRESH_URL, data={"refresh": tokens["refresh"]}, format="json")
        assert response.status_code == 200
        assert "access" in response.data

    def test_token_refresh_with_invalid_token_returns_401(self, api_client):
        response = api_client.post(TOKEN_REFRESH_URL, data={"refresh": "invalid.token.here"}, format="json")
        assert response.status_code == 401

    def test_token_verify_valid_token_returns_200(self, api_client, user):
        tokens = self._get_tokens(api_client, user)
        response = api_client.post(TOKEN_VERIFY_URL, data={"token": tokens["access"]}, format="json")
        assert response.status_code == 200

    def test_token_verify_invalid_token_returns_401(self, api_client):
        response = api_client.post(TOKEN_VERIFY_URL, data={"token": "fake.token"}, format="json")
        assert response.status_code == 401