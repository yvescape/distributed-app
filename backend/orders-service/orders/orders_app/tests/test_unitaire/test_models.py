# orders_app/tests/tests_unitaire/test_models.py
import uuid
import pytest
from decimal import Decimal
from django.utils import timezone
from orders_app.models.order import Order
from orders_app.models.order_item import OrderItem
from orders_app.models.order_address import OrderAddress
from orders_app.models.delivery_option import DeliveryOption
from orders_app.models.order_pricing import OrderPricing
from ..factories import (
    OrderFactory, OrderItemFactory, OrderAddressFactory,
    DeliveryOptionFactory, OrderPricingFactory
)


@pytest.mark.unit
class TestOrderModel:

    def test_order_creation(self, db):
        order = OrderFactory()
        assert order.pk is not None
        assert isinstance(order.id, uuid.UUID)

    def test_order_default_status_is_pending(self, db):
        order = OrderFactory()
        assert order.status == "pending"

    def test_order_default_total_is_zero(self, db):
        order = OrderFactory(total_amount=Decimal("0"))
        assert order.total_amount == Decimal("0")

    def test_order_str(self, db):
        order = OrderFactory()
        assert str(order) == f"Order {order.id}"

    def test_order_user_id_nullable(self, db):
        order = OrderFactory(user_id=None)
        assert order.user_id is None

    def test_order_status_choices(self, db):
        for status in ["pending", "confirmed", "cancelled"]:
            o = OrderFactory(status=status)
            assert o.status == status

    def test_order_timestamps(self, db):
        before = timezone.now()
        order = OrderFactory()
        after = timezone.now()
        assert before <= order.created_at <= after

    def test_order_updated_at_changes_on_save(self, db):
        order = OrderFactory()
        old = order.updated_at
        order.status = "confirmed"
        order.save()
        order.refresh_from_db()
        assert order.updated_at >= old


@pytest.mark.unit
class TestOrderItemModel:

    def test_order_item_creation(self, db):
        item = OrderItemFactory(price=Decimal("49.99"), quantity=2, subtotal=Decimal("99.98"))
        assert item.pk is not None
        assert isinstance(item.id, uuid.UUID)

    def test_order_item_str(self, db):
        item = OrderItemFactory(product_name="Dior Sauvage", quantity=3)
        assert str(item) == "Dior Sauvage x 3"

    def test_order_item_cascade_delete(self, db):
        item = OrderItemFactory()
        item_id = item.pk
        item.order.delete()
        assert not OrderItem.objects.filter(id=item_id).exists()

    def test_order_item_product_id_is_uuid(self, db):
        item = OrderItemFactory()
        assert isinstance(item.product_id, uuid.UUID)

    def test_order_item_default_quantity(self, db):
        item = OrderItemFactory()
        assert item.quantity >= 1


@pytest.mark.unit
class TestOrderAddressModel:

    def test_address_creation(self, db):
        address = OrderAddressFactory(city="Abidjan", address_line="Riviera 3")
        assert address.pk is not None
        assert address.city == "Abidjan"

    def test_address_cascade_delete(self, db):
        address = OrderAddressFactory()
        address_id = address.pk
        address.order.delete()
        assert not OrderAddress.objects.filter(id=address_id).exists()

    def test_address_one_to_one_constraint(self, db):
        from django.db import IntegrityError
        order = OrderFactory()
        OrderAddress.objects.create(order=order, city="Abidjan", address_line="Rue 1")
        with pytest.raises(IntegrityError):
            OrderAddress.objects.create(order=order, city="Bouaké", address_line="Rue 2")

    def test_address_postal_code_optional(self, db):
        address = OrderAddressFactory(postal_code="")
        assert address.postal_code == ""


@pytest.mark.unit
class TestDeliveryOptionModel:

    def test_delivery_option_creation(self, db):
        opt = DeliveryOptionFactory(name="Standard", amount=Decimal("2500.00"))
        assert opt.pk is not None
        assert opt.name == "Standard"

    def test_delivery_option_str(self, db):
        opt = DeliveryOptionFactory(name="Express", description="24h")
        assert str(opt) == "Express 24h"

    def test_delivery_option_default_currency_xof(self, db):
        opt = DeliveryOptionFactory()
        assert opt.currency == "XOF"

    def test_delivery_option_default_is_active(self, db):
        opt = DeliveryOptionFactory()
        assert opt.is_active is True

    def test_only_one_default_delivery_option(self, db):
        """Quand on définit une nouvelle option par défaut, l'ancienne perd is_default."""
        opt1 = DeliveryOptionFactory(is_default=True)
        assert opt1.is_default is True

        opt2 = DeliveryOptionFactory(is_default=True)
        opt1.refresh_from_db()

        assert opt2.is_default is True
        assert opt1.is_default is False

    def test_inactive_option_flag(self, db):
        opt = DeliveryOptionFactory(is_active=False)
        assert opt.is_active is False

    def test_position_ordering(self, db):
        opt1 = DeliveryOptionFactory(position=0)
        opt2 = DeliveryOptionFactory(position=1)
        opt3 = DeliveryOptionFactory(position=2)
        opts = list(DeliveryOption.objects.order_by("position"))
        assert opts[0].pk == opt1.pk
        assert opts[1].pk == opt2.pk
        assert opts[2].pk == opt3.pk


@pytest.mark.unit
class TestOrderPricingModel:

    def test_pricing_creation(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("50.00"), quantity=2, subtotal=Decimal("100.00"))
        delivery = DeliveryOptionFactory(amount=Decimal("2500.00"))

        pricing = OrderPricing.objects.create(
            order=order,
            delivery_option=delivery,
            currency="XOF",
        )

        pricing.refresh_from_db()
        assert pricing.subtotal == Decimal("100.00")
        assert pricing.delivery_price == Decimal("2500.00")
        assert pricing.total == Decimal("2600.00")

    def test_pricing_str(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("10"), quantity=1, subtotal=Decimal("10"))
        delivery = DeliveryOptionFactory()
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)
        assert str(pricing) == f"Pricing for order {order.id}"

    def test_pricing_cascade_delete(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("10"), quantity=1, subtotal=Decimal("10"))
        delivery = DeliveryOptionFactory()
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)
        pricing_id = pricing.pk
        order.delete()
        assert not OrderPricing.objects.filter(id=pricing_id).exists()

    def test_pricing_delivery_null_when_option_deleted(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("10"), quantity=1, subtotal=Decimal("10"))
        delivery = DeliveryOptionFactory()
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)
        delivery.delete()
        pricing.refresh_from_db()
        assert pricing.delivery_option is None

    def test_pricing_recalculates_on_save(self, db):
        order = OrderFactory()
        OrderItemFactory(order=order, price=Decimal("100"), quantity=1, subtotal=Decimal("100"))
        delivery = DeliveryOptionFactory(amount=Decimal("1500"))
        pricing = OrderPricing.objects.create(order=order, delivery_option=delivery)

        # Ajouter un item et re-sauvegarder
        OrderItemFactory(order=order, price=Decimal("50"), quantity=2, subtotal=Decimal("100"))
        pricing.save()
        pricing.refresh_from_db()

        assert pricing.subtotal == Decimal("200")
        assert pricing.total == Decimal("1700")