"""
Tests unitaires — Modèles (Order, OrderItem, DeliveryOption, OrderPricing, OrderAddress).
"""
import uuid
from decimal import Decimal

import pytest
from django.db import IntegrityError

from orders_app.models.order import Order
from orders_app.models.order_item import OrderItem
from orders_app.models.order_address import OrderAddress
from orders_app.models.order_pricing import OrderPricing
from orders_app.models.delivery_option import DeliveryOption
from ..factories import (
    OrderFactory, OrderItemFactory, OrderAddressFactory,
    DeliveryOptionFactory, OrderPricingFactory,
)
from ..conftest import USER_ID, PRODUCT_ID

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


class TestOrderModel:

    def test_create_order(self):
        order = OrderFactory(user_id=USER_ID)
        assert order.pk is not None
        assert order.status == "pending"
        assert order.user_id == USER_ID

    def test_default_status_is_pending(self):
        order = Order.objects.create(user_id=USER_ID)
        assert order.status == "pending"

    def test_str(self):
        order = OrderFactory()
        assert "Order" in str(order)

    def test_subtotal_property(self):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("50.00"), quantity=2, total=Decimal("100.00"))
        OrderItemFactory(order=order, price=Decimal("30.00"), quantity=1, total=Decimal("30.00"))
        assert order.subtotal == Decimal("130.00")

    def test_subtotal_empty_order(self):
        order = OrderFactory()
        assert order.subtotal == 0


class TestOrderItemModel:

    def test_create_item(self):
        item = OrderItemFactory()
        assert item.pk is not None
        assert item.quantity == 1

    def test_str(self):
        item = OrderItemFactory(product_name="Rose Noire", quantity=3)
        assert "Rose Noire" in str(item)
        assert "3" in str(item)


class TestOrderAddressModel:

    def test_create_address(self):
        addr = OrderAddressFactory()
        assert addr.first_name == "Jean"
        assert addr.city == "Abidjan"

    def test_str(self):
        addr = OrderAddressFactory(first_name="Marie", last_name="Koné", city="Bouaké")
        assert "Marie" in str(addr)
        assert "Bouaké" in str(addr)

    def test_one_address_per_order(self):
        order = OrderFactory()
        OrderAddressFactory(order=order)
        with pytest.raises(IntegrityError):
            OrderAddressFactory(order=order)


class TestDeliveryOptionModel:

    def test_create_option(self):
        opt = DeliveryOptionFactory(name="Express", amount=Decimal("5000.00"))
        assert opt.name == "Express"
        assert opt.is_active is True

    def test_default_flag_unique(self):
        """Un seul is_default=True à la fois."""
        opt1 = DeliveryOptionFactory(is_default=True)
        opt2 = DeliveryOptionFactory(is_default=True)
        opt1.refresh_from_db()
        assert opt1.is_default is False
        assert opt2.is_default is True

    def test_str(self):
        opt = DeliveryOptionFactory(name="Standard", description="3-5j")
        assert "Standard" in str(opt)


class TestOrderPricingModel:

    def test_calculate_and_save(self, delivery_option):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("100.00"), quantity=1, total=Decimal("100.00"))
        pricing = OrderPricing.objects.create(order=order)
        pricing.calculate_and_save()
        pricing.refresh_from_db()
        assert pricing.subtotal == Decimal("100.00")
        assert pricing.delivery_price == delivery_option.amount
        assert pricing.total == Decimal("100.00") + delivery_option.amount

    def test_assign_default_delivery(self, delivery_option):
        order = OrderFactory()
        pricing = OrderPricing.objects.create(order=order)
        pricing.assign_default_delivery()
        assert pricing.delivery_option == delivery_option

    def test_no_delivery_option_available(self):
        """Sans option de livraison active, delivery_price = 0."""
        order = OrderFactory()
        pricing = OrderPricing.objects.create(order=order)
        pricing.assign_default_delivery()
        assert pricing.delivery_price == Decimal("0")