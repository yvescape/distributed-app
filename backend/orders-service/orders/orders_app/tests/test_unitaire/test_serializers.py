# orders_app/tests/tests_unitaire/test_serializers.py
import pytest
import uuid
from decimal import Decimal
from orders_app.serializers.order import (
    OrderCreateSerializer, OrderDetailSerializer, OrderStatusUpdateSerializer
)
from orders_app.serializers.order_item import OrderItemSerializer
from orders_app.serializers.order_address import OrderAddressSerializer
from orders_app.serializers.delivery_option import DeliveryOptionSerializer
from orders_app.models.order_item import OrderItem
from orders_app.models.order_address import OrderAddress
from ..factories import OrderFactory, OrderItemFactory, OrderAddressFactory, DeliveryOptionFactory
from orders_app.serializers.order_pricing import OrderPricingSerializer
from orders_app.models.order_pricing import OrderPricing


def _valid_payload():
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


@pytest.mark.unit
class TestOrderCreateSerializer:

    def test_valid_payload_accepted(self, db):
        s = OrderCreateSerializer(data=_valid_payload())
        assert s.is_valid(), s.errors

    def test_create_order_with_items_and_address(self, db):
        s = OrderCreateSerializer(data=_valid_payload())
        assert s.is_valid()
        order = s.save()
        assert order.pk is not None
        assert OrderItem.objects.filter(order=order).count() == 1
        assert OrderAddress.objects.filter(order=order).exists()

    def test_total_amount_calculated_from_items(self, db):
        payload = _valid_payload()
        payload["items"] = [
            {"product_id": str(uuid.uuid4()), "product_name": "A", "price": "50.00", "quantity": 2},
            {"product_id": str(uuid.uuid4()), "product_name": "B", "price": "30.00", "quantity": 1},
        ]
        s = OrderCreateSerializer(data=payload)
        assert s.is_valid()
        order = s.save()
        assert order.total_amount == Decimal("130.00")

    def test_subtotal_calculated_per_item(self, db):
        s = OrderCreateSerializer(data=_valid_payload())
        assert s.is_valid()
        order = s.save()
        item = OrderItem.objects.filter(order=order).first()
        assert item.subtotal == item.price * item.quantity

    def test_missing_customer_name_rejected(self, db):
        payload = _valid_payload()
        del payload["customer_name"]
        s = OrderCreateSerializer(data=payload)
        assert not s.is_valid()
        assert "customer_name" in s.errors

    def test_missing_items_rejected(self, db):
        payload = _valid_payload()
        del payload["items"]
        s = OrderCreateSerializer(data=payload)
        assert not s.is_valid()
        assert "items" in s.errors

    def test_empty_items_rejected(self, db):
        payload = _valid_payload()
        payload["items"] = []
        s = OrderCreateSerializer(data=payload)
        assert not s.is_valid()

    def test_missing_address_rejected(self, db):
        payload = _valid_payload()
        del payload["address"]
        s = OrderCreateSerializer(data=payload)
        assert not s.is_valid()
        assert "address" in s.errors

    def test_invalid_email_rejected(self, db):
        payload = _valid_payload()
        payload["customer_email"] = "not-an-email"
        s = OrderCreateSerializer(data=payload)
        assert not s.is_valid()
        assert "customer_email" in s.errors

    def test_user_id_optional(self, db):
        payload = _valid_payload()
        payload["user_id"] = str(uuid.uuid4())
        s = OrderCreateSerializer(data=payload)
        assert s.is_valid(), s.errors

    def test_id_is_read_only(self, db):
        payload = _valid_payload()
        payload["id"] = "00000000-0000-0000-0000-000000000000"
        s = OrderCreateSerializer(data=payload)
        assert s.is_valid()
        order = s.save()
        assert str(order.id) != "00000000-0000-0000-0000-000000000000"


@pytest.mark.unit
class TestOrderDetailSerializer:

    def test_expected_fields(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order)
        OrderAddressFactory(order=order)
        data = OrderDetailSerializer(order).data
        expected = {
            "id", "user_id", "customer_name", "customer_email",
            "customer_phone", "status", "total_amount",
            "items", "address", "created_at",
        }
        assert expected.issubset(set(data.keys()))

    def test_items_nested(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order)
        OrderItemFactory(order=order)
        data = OrderDetailSerializer(order).data
        assert len(data["items"]) == 2

    def test_address_nested(self, db):
        order = OrderFactory()
        OrderAddressFactory(order=order, city="Abidjan")
        data = OrderDetailSerializer(order).data
        assert data["address"]["city"] == "Abidjan"


@pytest.mark.unit
class TestOrderStatusUpdateSerializer:

    def test_valid_status_accepted(self, db):
        order = OrderFactory()
        for status in ["pending", "confirmed", "cancelled"]:
            s = OrderStatusUpdateSerializer(order, data={"status": status})
            assert s.is_valid(), s.errors

    def test_invalid_status_rejected(self, db):
        order = OrderFactory()
        s = OrderStatusUpdateSerializer(order, data={"status": "shipped"})
        assert not s.is_valid()
        assert "status" in s.errors

    def test_only_status_field(self, db):
        order = OrderFactory()
        s = OrderStatusUpdateSerializer(order, data={"status": "confirmed"})
        assert s.is_valid()
        assert set(s.validated_data.keys()) == {"status"}


@pytest.mark.unit
class TestOrderItemSerializer:

    def test_valid_data(self, db):
        data = {
            "product_id": str(uuid.uuid4()),
            "product_name": "Chanel No 5",
            "price": "120.00",
            "quantity": 1,
        }
        s = OrderItemSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_subtotal_is_read_only(self, db):
        data = {
            "product_id": str(uuid.uuid4()),
            "product_name": "Test",
            "price": "50.00",
            "quantity": 2,
            "subtotal": "9999.00",  # tentatived'injection
        }
        s = OrderItemSerializer(data=data)
        assert s.is_valid()
        assert "subtotal" not in s.validated_data

    def test_expected_fields(self, db):
        item = OrderItemFactory()
        data = OrderItemSerializer(item).data
        assert set(data.keys()) == {"id", "product_id", "product_name", "price", "quantity", "subtotal"}


@pytest.mark.unit
class TestOrderAddressSerializer:

    def test_valid_data(self, db):
        data = {"city": "Abidjan", "address_line": "Riviera 3", "postal_code": "00225"}
        s = OrderAddressSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_postal_code_optional(self, db):
        data = {"city": "Bouaké", "address_line": "Centre-ville"}
        s = OrderAddressSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_missing_city_rejected(self, db):
        data = {"address_line": "Rue 1"}
        s = OrderAddressSerializer(data=data)
        assert not s.is_valid()
        assert "city" in s.errors

    def test_missing_address_line_rejected(self, db):
        """address_line est requis dans le modèle."""
        data = {"city": "Abidjan"}
        s = OrderAddressSerializer(data=data)
        assert not s.is_valid()
        assert "address_line" in s.errors


@pytest.mark.unit
class TestDeliveryOptionSerializer:

    def test_valid_data(self, db):
        data = {
            "name": "Livraison standard",
            "description": "3–5 jours",
            "amount": "2500.00",
            "currency": "XOF",
            "position": 0,
            "is_default": False,
            "is_active": True,
        }
        s = DeliveryOptionSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_expected_fields(self, db):
        opt = DeliveryOptionFactory()
        data = DeliveryOptionSerializer(opt).data
        expected = {"id", "name", "description", "amount", "currency", "position", "is_default", "is_active", "created_at"}
        assert set(data.keys()) == expected

    def test_id_and_created_at_read_only(self, db):
        opt = DeliveryOptionFactory()
        s = DeliveryOptionSerializer(opt, data={
            "id": str(uuid.uuid4()),
            "name": "Test",
            "description": "",
            "amount": "1000",
            "currency": "XOF",
            "position": 0,
            "is_default": False,
            "is_active": True,
        })
        assert s.is_valid()
        assert "id" not in s.validated_data
        assert "created_at" not in s.validated_data


# Ajouter cette classe à la fin du fichier
@pytest.mark.unit
class TestOrderPricingSerializer:

    def test_id_is_uuid(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("10"), quantity=1, subtotal=Decimal("10"))
        delivery = DeliveryOptionFactory()
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)
        data = OrderPricingSerializer(pricing).data
        uuid.UUID(data["id"])  # lève ValueError si invalide

    def test_expected_fields(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("10"), quantity=1, subtotal=Decimal("10"))
        delivery = DeliveryOptionFactory()
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)
        data = OrderPricingSerializer(pricing).data
        expected = {"id", "order", "delivery_option", "subtotal", "delivery_price", "total", "currency", "updated_at"}
        assert set(data.keys()) == expected

    def test_calculated_fields_are_read_only(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("50"), quantity=2, subtotal=Decimal("100"))
        delivery = DeliveryOptionFactory(amount=Decimal("1500"))
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)
        data = OrderPricingSerializer(pricing).data
        assert data["subtotal"] == "100.00"
        assert data["delivery_price"] == "1500.00"
        assert data["total"] == "1600.00"

    def test_totals_recalculated_on_save(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("100"), quantity=1, subtotal=Decimal("100"))
        delivery = DeliveryOptionFactory(amount=Decimal("2500"))
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)
        # Ajouter un item et re-sauvegarder
        OrderItemFactory(order=order, price=Decimal("50"), quantity=2, subtotal=Decimal("100"))
        pricing.save()
        pricing.refresh_from_db()
        assert pricing.subtotal == Decimal("200")
        assert pricing.total == Decimal("2700")