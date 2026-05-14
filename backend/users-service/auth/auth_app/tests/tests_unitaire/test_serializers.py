"""
Tests unitaires — Serializers (auth-service).
"""
import pytest
from django.contrib.auth import get_user_model
from auth_app.serializers.register import RegisterSerializer
from auth_app.serializers.user import UserSerializer
from auth_app.serializers.login import LoginSerializer
from auth_app.serializers.update_user import UpdateUserSerializer
from auth_app.serializers.audit_log import AuditLogSerializer
from auth_app.models.user_audit_log import UserAuditLog
from ..factories import UserFactory

User = get_user_model()

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


# ═══════════════════════════════════════════════════════════════════════
#  RegisterSerializer
# ═══════════════════════════════════════════════════════════════════════

class TestRegisterSerializer:

    def test_valid_registration(self):
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_mismatched_passwords(self):
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass456!",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()

    def test_short_password(self):
        data = {
            "email": "new@example.com",
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "password": "short",
            "password_confirm": "short",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_missing_email(self):
        data = {
            "username": "newuser",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_create_user_successfully(self):
        data = {
            "email": "created@example.com",
            "username": "createduser",
            "first_name": "Jane",
            "last_name": "Smith",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.pk is not None
        assert user.email == "created@example.com"
        assert user.check_password("StrongPass123!")

    def test_create_user_creates_audit_log(self):
        data = {
            "email": "audit@example.com",
            "username": "audituser",
            "first_name": "Audit",
            "last_name": "Test",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert UserAuditLog.objects.filter(user=user, action="CREATE").exists()

    def test_password_not_in_representation(self):
        data = {
            "email": "repr@example.com",
            "username": "repruser",
            "first_name": "Repr",
            "last_name": "Test",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        output = RegisterSerializer(user).data
        assert "password" not in output
        assert "password_confirm" not in output


# ═══════════════════════════════════════════════════════════════════════
#  UserSerializer
# ═══════════════════════════════════════════════════════════════════════

class TestUserSerializer:

    def test_expected_fields_present(self):
        user = UserFactory()
        data = UserSerializer(user).data
        expected = {
            "id", "email", "username", "first_name", "last_name",
            "is_active", "is_email_verified", "created_at",
        }
        assert set(data.keys()) == expected

    def test_does_not_expose_password(self):
        user = UserFactory()
        data = UserSerializer(user).data
        assert "password" not in data

    def test_read_only_id(self):
        user = UserFactory()
        data = UserSerializer(user).data
        assert "id" in data


# ═══════════════════════════════════════════════════════════════════════
#  UpdateUserSerializer
# ═══════════════════════════════════════════════════════════════════════

class TestUpdateUserSerializer:

    def test_valid_update(self):
        data = {"first_name": "Updated", "last_name": "Name"}
        serializer = UpdateUserSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_partial_update(self):
        data = {"first_name": "OnlyFirst"}
        serializer = UpdateUserSerializer(data=data, partial=True)
        assert serializer.is_valid(), serializer.errors

    def test_update_creates_audit_log(self):
        user = UserFactory()
        serializer = UpdateUserSerializer(user, data={"first_name": "Changed"}, partial=True)
        assert serializer.is_valid()
        serializer.save()
        assert UserAuditLog.objects.filter(user=user, action="UPDATE").exists()


# ═══════════════════════════════════════════════════════════════════════
#  AuditLogSerializer
# ═══════════════════════════════════════════════════════════════════════

class TestAuditLogSerializer:

    def test_serializes_log_with_email(self):
        user = UserFactory()
        log = UserAuditLog.objects.create(user=user, action="LOGIN", ip_address="1.2.3.4")
        data = AuditLogSerializer(log).data
        assert data["user_email"] == user.email
        assert data["action"] == "LOGIN"
        assert data["ip_address"] == "1.2.3.4"
        assert "id" in data
        assert "timestamp" in data