"""
Tests d'intégration — Cart items (OrderItem CRUD + quantity +/-).
"""
import uuid
from decimal import Decimal

import pytest

from orders_app.models.order import Order
from orders_app.models.order_item import OrderItem
from ..factories import OrderFactory, OrderItemFactory
from ..conftest import USER_ID, SESSION_ID, PRODUCT_ID, PRODUCT_ID_2

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

ITEMS_URL = "/orders_item/cart/items/"


class TestAddToCart:

    def test_add_item_authenticated(self, auth_client, mock_product_exists, mock_get_product_snapshot, delivery_option):
        resp = auth_client.post(ITEMS_URL, {"product_id": str(PRODUCT_ID)}, format="json")
        assert resp.status_code == 201
        assert Order.objects.filter(user_id=USER_ID, status="pending").exists()

    def test_add_item_guest(self, api_client, mock_product_exists, mock_get_product_snapshot, delivery_option):
        resp = api_client.post(ITEMS_URL, {"product_id": str(PRODUCT_ID), "session_id": str(SESSION_ID)}, format="json")
        assert resp.status_code == 201
        assert Order.objects.filter(session_id=SESSION_ID).exists()

    def test_add_same_product_increments_quantity(self, auth_client, mock_product_exists, mock_get_product_snapshot, delivery_option):
        auth_client.post(ITEMS_URL, {"product_id": str(PRODUCT_ID)}, format="json")
        auth_client.post(ITEMS_URL, {"product_id": str(PRODUCT_ID)}, format="json")
        order = Order.objects.get(user_id=USER_ID, status="pending")
        item = OrderItem.objects.get(order=order, product_id=PRODUCT_ID)
        assert item.quantity == 2

    def test_add_product_not_found(self, auth_client, mock_product_not_exists):
        resp = auth_client.post(ITEMS_URL, {"product_id": str(PRODUCT_ID)}, format="json")
        assert resp.status_code == 400

    def test_add_without_auth_or_session(self, api_client, mock_product_exists):
        resp = api_client.post(ITEMS_URL, {"product_id": str(PRODUCT_ID)}, format="json")
        assert resp.status_code == 400


class TestListCartItems:

    def test_list_items_authenticated(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        OrderItemFactory(order=order, product_id=PRODUCT_ID)
        OrderItemFactory(order=order, product_id=PRODUCT_ID_2)
        resp = auth_client.get(ITEMS_URL)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_list_empty_cart(self, auth_client):
        resp = auth_client.get(ITEMS_URL)
        assert resp.status_code == 200
        assert resp.data == []


class TestCartItemDetail:

    def test_delete_item(self, auth_client, delivery_option):
        order = OrderFactory(user_id=USER_ID)
        item1 = OrderItemFactory(order=order)
        item2 = OrderItemFactory(order=order)
        resp = auth_client.delete(f"{ITEMS_URL}{item1.id}/")
        assert resp.status_code == 204
        assert not OrderItem.objects.filter(pk=item1.id).exists()

    def test_delete_last_item_deletes_order(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        item = OrderItemFactory(order=order)
        auth_client.delete(f"{ITEMS_URL}{item.id}/")
        assert not Order.objects.filter(pk=order.id).exists()


class TestItemQuantity:

    def test_increment(self, auth_client, delivery_option):
        order = OrderFactory(user_id=USER_ID)
        item = OrderItemFactory(order=order, price=Decimal("50.00"), quantity=1, total=Decimal("50.00"))
        resp = auth_client.patch(
            f"{ITEMS_URL}{item.id}/quantity/",
            {"action": "increment", "amount": 2},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["quantity"] == 3
        assert Decimal(resp.data["total"]) == Decimal("150.00")

    def test_decrement(self, auth_client, delivery_option):
        order = OrderFactory(user_id=USER_ID)
        item = OrderItemFactory(order=order, price=Decimal("50.00"), quantity=3, total=Decimal("150.00"))
        resp = auth_client.patch(
            f"{ITEMS_URL}{item.id}/quantity/",
            {"action": "decrement", "amount": 1},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["quantity"] == 2

    def test_decrement_to_zero_deletes_item(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        item = OrderItemFactory(order=order, quantity=1)
        resp = auth_client.patch(
            f"{ITEMS_URL}{item.id}/quantity/",
            {"action": "decrement", "amount": 1},
            format="json",
        )
        assert resp.status_code == 200
        assert not OrderItem.objects.filter(pk=item.id).exists()

    def test_invalid_action(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        item = OrderItemFactory(order=order)
        resp = auth_client.patch(
            f"{ITEMS_URL}{item.id}/quantity/",
            {"action": "invalid"},
            format="json",
        )
        assert resp.status_code == 400


class TestProductInCart:

    def test_product_in_cart(self, auth_client):
        order = OrderFactory(user_id=USER_ID)
        OrderItemFactory(order=order, product_id=PRODUCT_ID, quantity=2)
        resp = auth_client.get(f"/orders_item/check/{PRODUCT_ID}/")
        assert resp.status_code == 200
        assert resp.data["in_cart"] is True
        assert resp.data["quantity"] == 2

    def test_product_not_in_cart(self, auth_client):
        resp = auth_client.get(f"/orders_item/check/{PRODUCT_ID}/")
        assert resp.status_code == 200
        assert resp.data["in_cart"] is False