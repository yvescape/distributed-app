"""
Fixtures partagées pour les tests du orders-service.
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from .factories import (
    OrderFactory, GuestOrderFactory, OrderItemFactory,
    OrderAddressFactory, DeliveryOptionFactory, OrderPricingFactory,
)

# ── Constantes ────────────────────────────────────────────────────────

USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
USER_ID_2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
SESSION_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PRODUCT_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
PRODUCT_ID_2 = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


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


@pytest.fixture
def internal_client():
    """Client avec le token interne pour les endpoints inter-services."""
    client = APIClient()
    client.credentials(HTTP_X_INTERNAL_TOKEN="test-internal-token")
    return client


# ── Données ───────────────────────────────────────────────────────────

@pytest.fixture
def delivery_option(db):
    return DeliveryOptionFactory()


@pytest.fixture
def order_with_items(db, delivery_option):
    """Commande pending avec 2 items, une adresse, et un pricing."""
    order = OrderFactory(user_id=USER_ID)
    OrderItemFactory(order=order, product_id=PRODUCT_ID, price=Decimal("50.00"), quantity=2, total=Decimal("100.00"))
    OrderItemFactory(order=order, product_id=PRODUCT_ID_2, price=Decimal("30.00"), quantity=1, total=Decimal("30.00"))
    OrderAddressFactory(order=order)
    OrderPricingFactory(order=order, delivery_option=delivery_option, subtotal=Decimal("130.00"),
                        delivery_price=delivery_option.amount, total=Decimal("130.00") + delivery_option.amount)
    return order


@pytest.fixture
def guest_order_with_items(db, delivery_option):
    """Commande guest pending avec 1 item."""
    order = GuestOrderFactory(session_id=SESSION_ID)
    OrderItemFactory(order=order, product_id=PRODUCT_ID, price=Decimal("50.00"), quantity=1, total=Decimal("50.00"))
    return order


@pytest.fixture
def mock_product_exists(mocker):
    return mocker.patch("orders_app.views.order_item.product_exists", return_value=True)


@pytest.fixture
def mock_product_not_exists(mocker):
    return mocker.patch("orders_app.views.order_item.product_exists", return_value=False)


@pytest.fixture
def mock_get_product_snapshot(mocker):
    return mocker.patch(
        "orders_app.views.order_item.get_product_snapshot",
        return_value={
            "price": Decimal("75.00"),
            "name": "Parfum Mocké",
            "image": "https://cdn.example.com/mock.jpg",
            "size": "50ml",
        },
    )