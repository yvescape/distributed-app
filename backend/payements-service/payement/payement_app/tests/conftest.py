# payement_app/tests/conftest.py
import uuid
import pytest
from rest_framework.test import APIClient
from .factories import PaymentFactory, SavedPrepaidCardFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client():
    """Client avec utilisateur authentifié simulé."""
    client = APIClient()
    user = type("FakeUser", (), {
        "id": uuid.uuid4(),
        "pk": 1,
        "is_staff": False,
        "is_superuser": False,
        "is_active": True,
        "is_authenticated": True,
    })()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client():
    """Client admin simulé."""
    client = APIClient()
    admin = type("FakeAdmin", (), {
        "id": uuid.uuid4(),
        "pk": 2,
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
        "is_authenticated": True,
    })()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def payment(db):
    return PaymentFactory()


@pytest.fixture
def failed_payment(db):
    return PaymentFactory(status="failed")


@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def saved_card(db, user_id):
    return SavedPrepaidCardFactory(user_id=user_id)


@pytest.fixture
def valid_payment_payload(db):
    return {
        "order_pricing_id": str(uuid.uuid4()),
        "amount": "2500",
        "currency": "XOF",
        "card_number": "1234567890123456",   # 16 chiffres → success
        "card_holder": "Kouadio Jean",
        "expiration_date": "12/27",
        "cvv": "123",
    }


@pytest.fixture
def invalid_card_payload(db):
    return {
        "order_pricing_id": str(uuid.uuid4()),
        "amount": "2500",
        "currency": "XOF",
        "card_number": "1234-5678-9012-3456",  # format invalide → failed
        "card_holder": "Kouadio Jean",
        "expiration_date": "12/27",
        "cvv": "123",
    }