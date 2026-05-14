"""
Tests unitaires — Serializers.
"""
import uuid
from decimal import Decimal

import pytest

from orders_app.serializers.order_item import OrderItemSerializer
from orders_app.serializers.order_address import OrderAddressSerializer
from orders_app.serializers.delivery_option import DeliveryOptionSerializer
from orders_app.serializers.order import OrderDetailSerializer
from ..factories import OrderFactory, OrderItemFactory, OrderAddressFactory, DeliveryOptionFactory, OrderPricingFactory

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


class TestOrderItemSerializer:

    def test_valid_create_data(self):
        data = {"product_id": str(uuid.uuid4()), "quantity": 1}
        s = OrderItemSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_read_only_fields_ignored(self):
        data = {"product_id": str(uuid.uuid4()), "price": "999.99", "total": "999.99"}
        s = OrderItemSerializer(data=data)
        assert s.is_valid()
        assert "price" not in s.validated_data
        assert "total" not in s.validated_data

    def test_serializes_item(self):
        item = OrderItemFactory()
        data = OrderItemSerializer(item).data
        assert data["product_name"] == item.product_name
        assert "session_id" not in data  # write_only


class TestOrderAddressSerializer:

    def test_valid_data(self):
        data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "mobile": "+225010101",
            "city": "Abidjan",
        }
        s = OrderAddressSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_session_id_write_only(self):
        addr = OrderAddressFactory()
        data = OrderAddressSerializer(addr).data
        assert "session_id" not in data


class TestDeliveryOptionSerializer:

    def test_serializes_option(self):
        opt = DeliveryOptionFactory()
        data = DeliveryOptionSerializer(opt).data
        expected = {"id", "name", "description", "amount", "currency", "position", "is_default"}
        assert set(data.keys()) == expected


class TestOrderDetailSerializer:

    def test_contains_nested_relations(self):
        order = OrderFactory()
        OrderItemFactory(order=order)
        OrderAddressFactory(order=order)
        OrderPricingFactory(order=order)
        data = OrderDetailSerializer(order).data
        assert "items" in data
        assert len(data["items"]) == 1
        assert "address" in data
        assert "pricing" in data
        assert "subtotal" in data