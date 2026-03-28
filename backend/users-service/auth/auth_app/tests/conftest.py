# tests/conftest.py
import pytest
from rest_framework.test import APIClient
from .factories import UserFactory, UserProfileFactory


# ── Clients HTTP ───────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Client DRF anonyme."""
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    """Client DRF authentifié en tant qu'utilisateur standard."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Client DRF authentifié en tant qu'admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client


# ── Utilisateurs ───────────────────────────────────────────────────────────────

@pytest.fixture
def user(db):
    """Utilisateur standard avec profil."""
    u = UserFactory()
    UserProfileFactory(user=u)
    return u


@pytest.fixture
def admin_user(db):
    """Utilisateur staff/superuser avec profil."""
    u = UserFactory(is_staff=True, is_superuser=True)
    UserProfileFactory(user=u)
    return u


@pytest.fixture
def inactive_user(db):
    """Utilisateur désactivé avec profil."""
    u = UserFactory(is_active=False)
    UserProfileFactory(user=u)
    return u


# ── Données d'inscription valides ─────────────────────────────────────────────

@pytest.fixture
def register_payload():
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "first_name": "John",
        "last_name": "Doe",
        "password": "StrongPass123!",
        "password_confirm": "StrongPass123!",
    }