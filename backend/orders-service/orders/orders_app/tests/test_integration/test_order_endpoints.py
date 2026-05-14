"""
Tests d'intégration — Order endpoints (list, detail, confirm, cancel, claim, cart count).
"""
import uuid
from decimal import Decimal

import pytest

from orders_app.models.order import Order
from ..factories import OrderFactory, OrderItemFactory, OrderAddressFactory, GuestOrderFactory
from ..conftest import USER_ID, USER_ID_2, SESSION_ID, PRODUCT_ID

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


class TestUserOrderList:

    URL = "/my/"

    def test_list_own_orders(self, auth_client):
        OrderFactory(user_id=USER_ID, status="confirmed")
        OrderFactory(user_id=USER_ID, status="pending")
        OrderFactory(user_id=USER_ID_2)  # autre user
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_list_guest_orders_by_session(self, api_client):
        order = GuestOrderFactory(session_id=SESSION_ID)
        resp = api_client.get(self.URL, {"session_id": str(SESSION_ID)})
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_list_empty_without_auth_or_session(self, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 200
        assert resp.data == []


class TestOrderDetail:

    def test_detail_own_order(self, auth_client, order_with_items):
        resp = auth_client.get(f"/{order_with_items.id}/")
        assert resp.status_code == 200
        assert resp.data["id"] == str(order_with_items.id)
        assert len(resp.data["items"]) == 2
        assert resp.data["address"] is not None
        assert resp.data["pricing"] is not None

    def test_detail_other_user_returns_404(self, auth_client_2, order_with_items):
        resp = auth_client_2.get(f"/{order_with_items.id}/")
        assert resp.status_code == 404

    def test_detail_guest_by_session(self, api_client, guest_order_with_items):
        resp = api_client.get(f"/{guest_order_with_items.id}/", {"session_id": str(SESSION_ID)})
        assert resp.status_code == 200


class TestOrderConfirm:

    def test_confirm_order_with_items_and_address(self, auth_client, order_with_items):
        resp = auth_client.put(f"/{order_with_items.id}/confirm/")
        assert resp.status_code == 200
        assert resp.data["status"] == "confirmed"

    def test_confirm_without_items_fails(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        OrderAddressFactory(order=order)
        resp = auth_client.put(f"/{order.id}/confirm/")
        assert resp.status_code == 400

    def test_confirm_without_address_fails(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        OrderItemFactory(order=order)
        resp = auth_client.put(f"/{order.id}/confirm/")
        assert resp.status_code == 400


class TestOrderCancel:

    def test_cancel_pending_order(self, auth_client, order_with_items):
        resp = auth_client.put(f"/{order_with_items.id}/cancel/")
        assert resp.status_code == 200
        assert resp.data["status"] == "cancelled"

    def test_cancel_confirmed_order(self, auth_client):
        order = OrderFactory(user_id=USER_ID, status="confirmed")
        resp = auth_client.put(f"/{order.id}/cancel/")
        assert resp.status_code == 200
        assert resp.data["status"] == "cancelled"

    def test_cancel_already_cancelled_fails(self, auth_client):
        order = OrderFactory(user_id=USER_ID, status="cancelled")
        resp = auth_client.put(f"/{order.id}/cancel/")
        assert resp.status_code == 404


class TestClaimGuestOrders:

    URL = "/claim/"

    def test_claim_guest_orders(self, auth_client):
        GuestOrderFactory(session_id=SESSION_ID)
        GuestOrderFactory(session_id=SESSION_ID)
        resp = auth_client.patch(self.URL, {"session_id": str(SESSION_ID)}, format="json")
        assert resp.status_code == 200
        assert resp.data["orders_claimed"] == 2
        assert Order.objects.filter(user_id=USER_ID).count() == 2

    def test_claim_without_session_id(self, auth_client):
        resp = auth_client.patch(self.URL, {}, format="json")
        assert resp.status_code == 400

    def test_claim_requires_auth(self, api_client):
        resp = api_client.patch(self.URL, {"session_id": str(SESSION_ID)}, format="json")
        assert resp.status_code == 401


class TestCartCount:

    URL = "/cart/count/"

    def test_cart_count_with_items(self, auth_client, order_with_items):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        assert resp.data["count"] == 3  # 2 + 1

    def test_cart_count_empty(self, auth_client):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        assert resp.data["count"] == 0

    def test_cart_count_guest(self, api_client, guest_order_with_items):
        resp = api_client.get(self.URL, {"session_id": str(SESSION_ID)})
        assert resp.status_code == 200
        assert resp.data["count"] == 1