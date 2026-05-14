"""
Fixtures partagées pour tous les tests du interaction-service.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings

from interation_app.utils.authentication import JWTUser


# ── Constantes réutilisables ──────────────────────────────────────────

PRODUCT_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PRODUCT_ID_2 = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
USER_ID_2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
USER_EMAIL = "testeur@example.com"
USER_EMAIL_2 = "autre@example.com"


# ── Helpers ───────────────────────────────────────────────────────────

def make_jwt_token(user_id, email="test@example.com", is_staff=False):
    """Génère un vrai JWT signé avec la SECRET_KEY de test."""
    token = AccessToken()
    token["user_id"] = str(user_id)
    token["email"] = email
    token["is_staff"] = is_staff
    token.set_exp(from_time=datetime.now(timezone.utc), lifetime=timedelta(minutes=30))
    return str(token)


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Client DRF sans authentification."""
    return APIClient()


@pytest.fixture
def auth_client():
    """Client DRF authentifié (user 1)."""
    client = APIClient()
    token = make_jwt_token(USER_ID, USER_EMAIL)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def auth_client_2():
    """Client DRF authentifié (user 2)."""
    client = APIClient()
    token = make_jwt_token(USER_ID_2, USER_EMAIL_2)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def mock_product_exists(mocker):
    """Mock product_exists → True dans toutes les vues."""
    targets = [
        "interation_app.views.comment.product_exists",
        "interation_app.views.like.product_exists",
        "interation_app.views.rating.product_exists",
    ]
    mocks = [mocker.patch(t, return_value=True) for t in targets]
    return mocks[0]


@pytest.fixture
def mock_product_not_exists(mocker):
    """Mock product_exists → False dans toutes les vues."""
    targets = [
        "interation_app.views.comment.product_exists",
        "interation_app.views.like.product_exists",
        "interation_app.views.rating.product_exists",
    ]
    mocks = [mocker.patch(t, return_value=False) for t in targets]
    return mocks[0]