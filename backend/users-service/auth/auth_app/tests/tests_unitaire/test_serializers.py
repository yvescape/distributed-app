# tests/unit/test_serializers.py
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from auth_app.serializers.register import RegisterSerializer
from auth_app.serializers.login import LoginSerializer
from auth_app.serializers.user import UserSerializer
from auth_app.serializers.update_user import UpdateUserSerializer
from auth_app.serializers.profile import ProfileSerializer
from auth_app.models.user_audit_log import UserAuditLog
from auth_app.models.user_profile import UserProfile
from ..factories import UserFactory, UserProfileFactory

User = get_user_model()


# ── RegisterSerializer ─────────────────────────────────────────────────────────

@pytest.mark.unit
class TestRegisterSerializer:

    def _valid_data(self, overrides=None):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        if overrides:
            data.update(overrides)
        return data

    def test_valid_data_is_accepted(self, db):
        s = RegisterSerializer(data=self._valid_data())
        assert s.is_valid(), s.errors

    def test_mismatched_passwords_rejected(self, db):
        s = RegisterSerializer(data=self._valid_data({"password_confirm": "WrongPass!"}))
        assert not s.is_valid()
        assert "non_field_errors" in s.errors

    def test_password_too_short_rejected(self, db):
        s = RegisterSerializer(data=self._valid_data({"password": "short", "password_confirm": "short"}))
        assert not s.is_valid()
        assert "password" in s.errors

    def test_duplicate_email_rejected(self, db):
        UserFactory(email="newuser@example.com")
        s = RegisterSerializer(data=self._valid_data())
        assert not s.is_valid()
        assert "email" in s.errors

    def test_duplicate_username_rejected(self, db):
        UserFactory(username="newuser")
        s = RegisterSerializer(data=self._valid_data())
        assert not s.is_valid()
        assert "username" in s.errors

    def test_create_user_creates_profile(self, db):
        s = RegisterSerializer(data=self._valid_data())
        assert s.is_valid()
        user = s.save()
        assert UserProfile.objects.filter(user=user).exists()

    def test_create_user_creates_audit_log(self, db):
        s = RegisterSerializer(data=self._valid_data())
        assert s.is_valid()
        user = s.save()
        assert UserAuditLog.objects.filter(user=user, action="CREATE").exists()

    def test_password_not_in_response_fields(self, db):
        s = RegisterSerializer(data=self._valid_data())
        assert s.is_valid()
        user = s.save()
        out = RegisterSerializer(user)
        assert "password" not in out.data
        assert "password_confirm" not in out.data

    def test_id_is_read_only(self, db):
        s = RegisterSerializer(data=self._valid_data({"id": "00000000-0000-0000-0000-000000000000"}))
        assert s.is_valid()
        user = s.save()
        # L'id imposé dans la requête ne doit pas être utilisé
        assert str(user.id) != "00000000-0000-0000-0000-000000000000"

    def test_missing_required_field_rejected(self, db):
        data = self._valid_data()
        data.pop("email")
        s = RegisterSerializer(data=data)
        assert not s.is_valid()
        assert "email" in s.errors


# ── LoginSerializer ────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestLoginSerializer:

    def test_valid_credentials_return_tokens(self, db):
        user = UserFactory(email="login@example.com")
        s = LoginSerializer(data={"email": "login@example.com", "password": "StrongPass123!"})
        assert s.is_valid(), s.errors
        assert "access" in s.validated_data
        assert "refresh" in s.validated_data

    def test_wrong_password_rejected(self, db):
        UserFactory(email="login@example.com")
        s = LoginSerializer(data={"email": "login@example.com", "password": "WrongPass!"})
        assert not s.is_valid()
        assert "non_field_errors" in s.errors

    def test_unknown_email_rejected(self, db):
        s = LoginSerializer(data={"email": "ghost@example.com", "password": "StrongPass123!"})
        assert not s.is_valid()

    def test_inactive_user_rejected(self, db):
        UserFactory(email="inactive@example.com", is_active=False)
        s = LoginSerializer(data={"email": "inactive@example.com", "password": "StrongPass123!"})
        assert not s.is_valid()
        error_text = str(s.errors)
        assert "désactivé" in error_text

    def test_login_creates_audit_log(self, db):
        user = UserFactory(email="audit@example.com")
        s = LoginSerializer(data={"email": "audit@example.com", "password": "StrongPass123!"})
        assert s.is_valid()
        assert UserAuditLog.objects.filter(user=user, action="LOGIN").exists()

    def test_invalid_email_format_rejected(self):
        s = LoginSerializer(data={"email": "not-an-email", "password": "StrongPass123!"})
        assert not s.is_valid()
        assert "email" in s.errors


# ── UserSerializer ─────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestUserSerializer:

    def test_expected_fields_present(self, db):
        user = UserFactory()
        UserProfileFactory(user=user)
        data = UserSerializer(user).data
        expected = {"id", "email", "username", "first_name", "last_name",
                    "is_active", "is_email_verified", "created_at", "profile"}
        assert set(data.keys()) == expected

    def test_profile_nested_when_exists(self, db):
        user = UserFactory()
        UserProfileFactory(user=user, country="Côte d'Ivoire")
        data = UserSerializer(user).data
        assert data["profile"] is not None
        assert data["profile"]["country"] == "Côte d'Ivoire"

    def test_profile_none_when_missing(self, db):
        user = UserFactory()  # pas de profil créé
        data = UserSerializer(user).data
        assert data["profile"] is None


# ── UpdateUserSerializer ───────────────────────────────────────────────────────

@pytest.mark.unit
class TestUpdateUserSerializer:

    def test_update_first_and_last_name(self, db):
        user = UserFactory(first_name="Old", last_name="Name")
        s = UpdateUserSerializer(user, data={"first_name": "New", "last_name": "Name"})
        assert s.is_valid(), s.errors
        updated = s.save()
        assert updated.first_name == "New"

    def test_update_creates_audit_log(self, db):
        user = UserFactory()
        s = UpdateUserSerializer(user, data={"first_name": "Updated", "last_name": "User"})
        assert s.is_valid()
        s.save()
        assert UserAuditLog.objects.filter(user=user, action="UPDATE").exists()

    def test_cannot_update_email_via_this_serializer(self, db):
        user = UserFactory(email="original@example.com")
        s = UpdateUserSerializer(user, data={"email": "hacked@example.com", "first_name": "X", "last_name": "Y"})
        assert s.is_valid()
        s.save()
        user.refresh_from_db()
        # L'email ne doit pas avoir changé
        assert user.email == "original@example.com"


# ── ProfileSerializer ──────────────────────────────────────────────────────────

@pytest.mark.unit
class TestProfileSerializer:

    def test_valid_profile_data(self, db):
        data = {"phone_number": "+2250102030405", "bio": "Dev", "country": "CI", "avatar": "https://cdn.example.com/a.jpg"}
        s = ProfileSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_all_fields_optional(self, db):
        s = ProfileSerializer(data={})
        assert s.is_valid(), s.errors

    def test_expected_fields(self, db):
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        data = ProfileSerializer(profile).data
        assert set(data.keys()) == {"phone_number", "avatar", "bio", "country"}