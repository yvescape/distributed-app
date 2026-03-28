# orders_app/tests/tests_integration/test_order_endpoints.py
import pytest
import uuid
from decimal import Decimal
from rest_framework.test import APIClient
from orders_app.models.order import Order
from orders_app.models.order_item import OrderItem
from orders_app.models.order_address import OrderAddress
from ..factories import OrderFactory, OrderItemFactory, OrderAddressFactory


ORDERS_URL = "/api/orders/"
MY_ORDERS_URL = "/api/orders/my/"


def detail_url(pk):
    return f"/api/orders/{pk}/"


def status_url(pk):
    return f"/api/orders/{pk}/status/"


@pytest.mark.integration
@pytest.mark.django_db
class TestOrderCreateEndpoint:

    def test_create_order_returns_201(self, api_client, valid_order_payload):
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert response.status_code == 201

    def test_create_order_no_auth_required(self, api_client, valid_order_payload):
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert response.status_code == 201

    def test_create_order_persists_in_db(self, api_client, valid_order_payload):
        api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert Order.objects.filter(customer_email="jean@example.com").exists()

    def test_create_order_creates_items(self, api_client, valid_order_payload):
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        order_id = response.data["id"]
        assert OrderItem.objects.filter(order_id=order_id).count() == 1

    def test_create_order_creates_address(self, api_client, valid_order_payload):
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        order_id = response.data["id"]
        assert OrderAddress.objects.filter(order_id=order_id).exists()

    def test_create_order_calculates_total(self, api_client, valid_order_payload):
        # items: 49.99 × 2 = 99.98
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        order = Order.objects.get(id=response.data["id"])
        assert order.total_amount == Decimal("99.98")

    def test_create_order_default_status_pending(self, api_client, valid_order_payload):
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        order = Order.objects.get(id=response.data["id"])
        assert order.status == "pending"

    def test_create_order_missing_items_returns_400(self, api_client, valid_order_payload):
        del valid_order_payload["items"]
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert response.status_code == 400

    def test_create_order_missing_address_returns_400(self, api_client, valid_order_payload):
        del valid_order_payload["address"]
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert response.status_code == 400

    def test_create_order_invalid_email_returns_400(self, api_client, valid_order_payload):
        valid_order_payload["customer_email"] = "not-valid"
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert response.status_code == 400

    def test_create_order_with_user_id(self, api_client, valid_order_payload):
        valid_order_payload["user_id"] = str(uuid.uuid4())
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert response.status_code == 201

    def test_create_order_multiple_items(self, api_client, valid_order_payload):
        valid_order_payload["items"].append({
            "product_id": str(uuid.uuid4()),
            "product_name": "Chanel No 5",
            "price": "120.00",
            "quantity": 1,
        })
        response = api_client.post(ORDERS_URL, data=valid_order_payload, format="json")
        assert response.status_code == 201
        order_id = response.data["id"]
        assert OrderItem.objects.filter(order_id=order_id).count() == 2


@pytest.mark.integration
@pytest.mark.django_db
class TestOrderDetailEndpoint:

    def test_detail_returns_200(self, api_client, order):
        response = api_client.get(detail_url(order.id))
        assert response.status_code == 200

    def test_detail_no_auth_required(self, api_client, order):
        response = api_client.get(detail_url(order.id))
        assert response.status_code == 200

    def test_detail_returns_correct_order(self, api_client, order):
        response = api_client.get(detail_url(order.id))
        assert response.data["id"] == str(order.id)
        assert response.data["customer_email"] == order.customer_email

    def test_detail_contains_items(self, api_client, order):
        response = api_client.get(detail_url(order.id))
        assert len(response.data["items"]) == 2

    def test_detail_contains_address(self, api_client, order):
        response = api_client.get(detail_url(order.id))
        assert response.data["address"]["city"] == "Abidjan"

    def test_detail_nonexistent_returns_404(self, api_client, db):
        response = api_client.get(detail_url(uuid.uuid4()))
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestOrderStatusUpdateEndpoint:

    def test_update_status_to_confirmed(self, admin_client, order):
        response = admin_client.patch(status_url(order.id), data={"status": "confirmed"}, format="json")
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == "confirmed"

    def test_update_status_to_cancelled(self, admin_client, order):
        response = admin_client.patch(status_url(order.id), data={"status": "cancelled"}, format="json")
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == "cancelled"

    def test_update_invalid_status_returns_400(self, admin_client, order):
        response = admin_client.patch(status_url(order.id), data={"status": "shipped"}, format="json")
        assert response.status_code == 400

    def test_update_nonexistent_order_returns_404(self, admin_client, db):
        response = admin_client.patch(status_url(uuid.uuid4()), data={"status": "confirmed"}, format="json")
        assert response.status_code == 404

    def test_update_status_unauthenticated_returns_401(self, api_client, order):
        response = api_client.patch(status_url(order.id), data={"status": "confirmed"}, format="json")
        assert response.status_code == 401

    def test_update_status_non_admin_returns_403(self, regular_client, order):
        response = regular_client.patch(status_url(order.id), data={"status": "confirmed"}, format="json")
        assert response.status_code == 403