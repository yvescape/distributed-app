# orders_app/tests/conftest.py
import uuid
import pytest
from rest_framework.test import APIClient
from .factories import (
    OrderFactory, OrderItemFactory, OrderAddressFactory,
    DeliveryOptionFactory, OrderPricingFactory
)


# ── Clients HTTP ───────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client():
    """Client simulant un admin (pas de modèle User local dans ce service)."""
    client = APIClient()
    admin = type("FakeAdmin", (), {
        "id": uuid.uuid4(),
        "pk": 1,
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
        "is_authenticated": True,
    })()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def regular_client():
    """Client authentifié mais non admin."""
    client = APIClient()
    user = type("FakeUser", (), {
        "id": uuid.uuid4(),
        "pk": 2,
        "is_staff": False,
        "is_superuser": False,
        "is_active": True,
        "is_authenticated": True,
    })()
    client.force_authenticate(user=user)
    return client


# ── Données ────────────────────────────────────────────────────────────────────

@pytest.fixture
def order(db):
    o = OrderFactory()
    OrderItemFactory(order=o, price="49.99", quantity=2, subtotal="99.98")
    OrderItemFactory(order=o, price="29.99", quantity=1, subtotal="29.99")
    OrderAddressFactory(order=o)
    o.total_amount = "129.97"
    o.save()
    return o


@pytest.fixture
def delivery_option(db):
    return DeliveryOptionFactory(is_active=True)


@pytest.fixture
def default_delivery(db):
    return DeliveryOptionFactory(is_default=True, is_active=True)


@pytest.fixture
def valid_order_payload(db):
    """Payload complet pour créer une commande."""
    return {
        "customer_name": "Kouadio Jean",
        "customer_email": "jean@example.com",
        "customer_phone": "+2250102030405",
        "items": [
            {
                "product_id": str(uuid.uuid4()),
                "product_name": "Dior Sauvage",
                "price": "49.99",
                "quantity": 2,
            }
        ],
        "address": {
            "city": "Abidjan",
            "address_line": "Cocody Riviera 3",
            "postal_code": "00225",
        },
    }