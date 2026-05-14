"""
Fixtures partagées pour les tests du payment-service.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from .factories import PaymentFactory, SavedPrepaidCardFactory

# ── Constantes ────────────────────────────────────────────────────────

USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
USER_ID_2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
ORDER_PRICING_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
ORDER_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


# ── Helpers ───────────────────────────────────────────────────────────

def make_jwt_token(user_id, email="test@example.com"):
    token = AccessToken()
    token["user_id"] = str(user_id)
    token["email"] = email
    token.set_exp(from_time=datetime.now(timezone.utc), lifetime=timedelta(minutes=30))
    return str(token)


# ── Clients ───────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client():
    client = APIClient()
    token = make_jwt_token(USER_ID)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def auth_client_2():
    client = APIClient()
    token = make_jwt_token(USER_ID_2)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


# ── Data ──────────────────────────────────────────────────────────────

@pytest.fixture
def payment(db):
    return PaymentFactory(order_pricing_id=ORDER_PRICING_ID)


@pytest.fixture
def saved_card(db):
    return SavedPrepaidCardFactory(user_id=USER_ID)


@pytest.fixture
def valid_payment_payload():
    return {
        "order_pricing_id": str(ORDER_PRICING_ID),
        "order_id": str(ORDER_ID),
        "amount": "15000",
        "currency": "FCFA",
        "card_number": "1234567890123456",  # 16 digits → success
        "card_holder": "Jean Dupont",
        "expiration_date": "12/28",
        "cvv": "123",
    }


@pytest.fixture
def invalid_card_payload():
    return {
        "order_pricing_id": str(ORDER_PRICING_ID),
        "order_id": str(ORDER_ID),
        "amount": "15000",
        "currency": "FCFA",
        "card_number": "INVALID-CARD",  # not 16 digits → failed
        "card_holder": "Jean Dupont",
        "expiration_date": "12/28",
        "cvv": "123",
    }


@pytest.fixture
def mock_order_confirm_success(mocker):
    """Mock l'appel HTTP vers orders-service → 200."""
    return mocker.patch(
        "payement_app.views.payment.requests.patch",
        return_value=mocker.Mock(status_code=200, text="OK"),
    )


@pytest.fixture
def mock_order_confirm_failure(mocker):
    """Mock l'appel HTTP vers orders-service → 500."""
    return mocker.patch(
        "payement_app.views.payment.requests.patch",
        return_value=mocker.Mock(status_code=500, text="Internal Server Error"),
    )