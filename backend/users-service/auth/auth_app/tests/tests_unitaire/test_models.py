# tests/unit/test_models.py
import pytest
import uuid
from django.utils import timezone
from auth_app.models.user_audit_log import UserAuditLog
from auth_app.models.user_profile import UserProfile
from ..factories import UserFactory, UserProfileFactory, UserAuditLogFactory


@pytest.mark.unit
class TestUserModel:

    def test_user_creation_with_required_fields(self, db):
        user = UserFactory(
            email="test@example.com",
            username="testuser",
            first_name="Jane",
            last_name="Doe",
        )
        assert user.pk is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_user_default_flags(self, db):
        user = UserFactory()
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_email_verified is False

    def test_user_password_is_hashed(self, db):
        user = UserFactory()
        # Le mot de passe ne doit jamais être stocké en clair
        assert user.password != "StrongPass123!"
        assert user.check_password("StrongPass123!")

    def test_user_str_returns_email(self, db):
        user = UserFactory(email="display@example.com")
        assert str(user) == "display@example.com"

    def test_user_username_field_is_email(self, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        assert User.USERNAME_FIELD == "email"

    def test_user_required_fields_contains_username(self, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        assert "username" in User.REQUIRED_FIELDS

    def test_user_email_is_unique(self, db):
        from django.db import IntegrityError
        UserFactory(email="unique@example.com")
        with pytest.raises(IntegrityError):
            UserFactory(email="unique@example.com")

    def test_user_username_is_unique(self, db):
        from django.db import IntegrityError
        UserFactory(username="uniqueuser")
        with pytest.raises(IntegrityError):
            UserFactory(username="uniqueuser")

    def test_user_timestamps_set_on_creation(self, db):
        before = timezone.now()
        user = UserFactory()
        after = timezone.now()
        assert before <= user.created_at <= after

    def test_updated_at_changes_on_save(self, db):
        user = UserFactory()
        old_updated_at = user.updated_at
        user.first_name = "Updated"
        user.save()
        user.refresh_from_db()
        assert user.updated_at >= old_updated_at


@pytest.mark.unit
class TestUserProfileModel:

    def test_profile_creation(self, db):
        user = UserFactory()
        profile = UserProfileFactory(user=user, bio="Dev Django", country="France")
        assert profile.user == user
        assert profile.bio == "Dev Django"
        assert profile.country == "France"

    def test_profile_str(self, db):
        user = UserFactory(email="profil@example.com")
        profile = UserProfileFactory(user=user)
        assert str(profile) == f"Profile of {user.email}"

    def test_profile_cascade_delete(self, db):
        user = UserFactory()
        UserProfileFactory(user=user)
        user_id = user.pk
        user.delete()
        assert not UserProfile.objects.filter(user_id=user_id).exists()

    def test_profile_optional_fields_default_blank(self, db):
        user = UserFactory()
        profile = UserProfile.objects.create(user=user)
        assert profile.phone_number == ""
        assert profile.avatar == ""
        assert profile.bio == ""
        assert profile.country == ""

    def test_profile_one_to_one_constraint(self, db):
        from django.db import IntegrityError
        user = UserFactory()
        UserProfile.objects.create(user=user)
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user)


@pytest.mark.unit
class TestUserAuditLogModel:

    def test_audit_log_creation(self, db):
        log = UserAuditLogFactory(action="LOGIN", ip_address="192.168.1.1")
        assert isinstance(log.id, uuid.UUID)
        assert log.action == "LOGIN"
        assert log.ip_address == "192.168.1.1"

    def test_audit_log_str(self, db):
        user = UserFactory(email="audit@example.com")
        log = UserAuditLogFactory(user=user, action="UPDATE")
        assert str(log) == "audit@example.com - UPDATE"

    def test_audit_log_cascade_delete(self, db):
        user = UserFactory()
        log = UserAuditLogFactory(user=user)
        log_id = log.pk
        user.delete()
        assert not UserAuditLog.objects.filter(id=log_id).exists()

    def test_audit_log_all_actions_valid(self, db):
        user = UserFactory()
        for action in ["CREATE", "UPDATE", "DELETE", "LOGIN"]:
            log = UserAuditLog.objects.create(user=user, action=action)
            assert log.action == action

    def test_audit_log_timestamp_auto_set(self, db):
        before = timezone.now()
        log = UserAuditLogFactory()
        after = timezone.now()
        assert before <= log.timestamp <= after

    def test_audit_log_ip_address_nullable(self, db):
        log = UserAuditLogFactory(ip_address=None)
        assert log.ip_address is None