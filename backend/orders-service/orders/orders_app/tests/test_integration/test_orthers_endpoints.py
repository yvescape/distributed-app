"""
Tests d'intégration — Address, Delivery, Pricing, Internal, Health.
"""
import uuid
from decimal import Decimal

import pytest

from orders_app.models.order import Order
from orders_app.models.order_address import OrderAddress
from orders_app.models.order_pricing import OrderPricing
from ..factories import (
    OrderFactory, OrderItemFactory, OrderAddressFactory,
    DeliveryOptionFactory, OrderPricingFactory, GuestOrderFactory,
)
from ..conftest import USER_ID, SESSION_ID, PRODUCT_ID

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


# ═══════════════════════════════════════════════════════════════════════
#  Address
# ═══════════════════════════════════════════════════════════════════════

class TestOrderAddress:

    URL = "/orders_address/"

    def test_create_address_authenticated(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        OrderItemFactory(order=order)
        resp = auth_client.post(self.URL, {
            "first_name": "Jean", "last_name": "Koné",
            "mobile": "+225010101", "city": "Abidjan",
        }, format="json")
        assert resp.status_code == 201
        assert OrderAddress.objects.filter(order=order).exists()

    def test_update_existing_address(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        OrderItemFactory(order=order)
        OrderAddressFactory(order=order, first_name="Old")
        resp = auth_client.post(self.URL, {
            "first_name": "New", "last_name": "Name",
            "mobile": "+225010101", "city": "Abidjan",
        }, format="json")
        assert resp.status_code == 201
        order.refresh_from_db()
        assert order.address.first_name == "New"

    def test_create_address_no_pending_order(self, auth_client):
        resp = auth_client.post(self.URL, {
            "first_name": "X", "last_name": "Y",
            "mobile": "0", "city": "Z",
        }, format="json")
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════
#  Delivery Options
# ═══════════════════════════════════════════════════════════════════════

class TestDeliveryOptions:

    URL = "/delivery-options/"

    def test_list_active_options(self, api_client, delivery_option):
        DeliveryOptionFactory(name="Express", amount=Decimal("5000"), is_default=False, position=1)
        resp = api_client.get(self.URL)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_inactive_option_not_listed(self, api_client):
        DeliveryOptionFactory(is_active=False)
        resp = api_client.get(self.URL)
        assert resp.status_code == 200
        assert len(resp.data) == 0

    def test_detail_option(self, api_client, delivery_option):
        resp = api_client.get(f"{self.URL}{delivery_option.id}/")
        assert resp.status_code == 200
        assert resp.data["name"] == delivery_option.name


# ═══════════════════════════════════════════════════════════════════════
#  Pricing
# ═══════════════════════════════════════════════════════════════════════

class TestOrderPricing:

    def test_pricing_detail(self, auth_client, order_with_items):
        pricing = order_with_items.pricing
        resp = auth_client.get(f"/{order_with_items.id}/pricing/{pricing.id}/")
        assert resp.status_code == 200
        assert "subtotal" in resp.data

    def test_update_delivery_option(self, auth_client, order_with_items):
        express = DeliveryOptionFactory(name="Express", amount=Decimal("5000"), is_default=False, position=1)
        resp = auth_client.patch(
            f"/{order_with_items.id}/pricing/delivery/",
            {"delivery_option_id": str(express.id)},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["delivery_option"]["name"] == "Express"
        assert Decimal(resp.data["delivery_price"]) == Decimal("5000.00")

    def test_update_delivery_invalid_option(self, auth_client, order_with_items):
        resp = auth_client.patch(
            f"/{order_with_items.id}/pricing/delivery/",
            {"delivery_option_id": str(uuid.uuid4())},
            format="json",
        )
        assert resp.status_code == 400

    def test_update_delivery_missing_id(self, auth_client, order_with_items):
        resp = auth_client.patch(
            f"/{order_with_items.id}/pricing/delivery/",
            {},
            format="json",
        )
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════
#  Internal endpoints
# ═══════════════════════════════════════════════════════════════════════

class TestInternalEndpoints:

    def test_internal_confirm(self, internal_client, order_with_items):
        resp = internal_client.patch(f"/internal/{order_with_items.id}/confirm/")
        assert resp.status_code == 200
        assert resp.data["status"] == "confirmed"

    def test_internal_cancel(self, internal_client, order_with_items):
        resp = internal_client.patch(f"/internal/{order_with_items.id}/cancel/")
        assert resp.status_code == 200
        assert resp.data["status"] == "cancelled"

    def test_internal_without_token_forbidden(self, api_client, order_with_items):
        resp = api_client.patch(f"/internal/{order_with_items.id}/confirm/")
        assert resp.status_code in (401, 403)

    def test_internal_wrong_token_forbidden(self, order_with_items):
        from rest_framework.test import APIClient
        client = APIClient()
        client.credentials(HTTP_X_INTERNAL_TOKEN="wrong-token")
        resp = client.patch(f"/internal/{order_with_items.id}/confirm/")
        assert resp.status_code in (401, 403)

    def test_internal_confirm_without_items_fails(self, internal_client):
        order = OrderFactory(user_id=USER_ID)
        OrderAddressFactory(order=order)
        resp = internal_client.patch(f"/internal/{order.id}/confirm/")
        assert resp.status_code == 400

    def test_internal_confirm_without_address_fails(self, internal_client):
        order = OrderFactory(user_id=USER_ID)
        OrderItemFactory(order=order)
        resp = internal_client.patch(f"/internal/{order.id}/confirm/")
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════════
#  Health
# ═══════════════════════════════════════════════════════════════════════

class TestHealthCheck:

    def test_health_returns_ok(self, api_client):
        resp = api_client.get("/health/")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}