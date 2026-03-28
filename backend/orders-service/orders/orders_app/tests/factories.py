# orders_app/tests/factories.py
import uuid
import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from orders_app.models.order import Order
from orders_app.models.order_item import OrderItem
from orders_app.models.order_address import OrderAddress
from orders_app.models.delivery_option import DeliveryOption
from orders_app.models.order_pricing import OrderPricing


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    customer_name = factory.Faker("name")
    customer_email = factory.Faker("email")
    customer_phone = factory.Faker("phone_number")
    status = "pending"
    total_amount = Decimal("0.00")


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    product_id = factory.LazyFunction(uuid.uuid4)
    product_name = factory.Sequence(lambda n: f"Parfum Test {n}")
    price = Decimal("49.99")
    quantity = 1
    subtotal = Decimal("49.99")


class OrderAddressFactory(DjangoModelFactory):
    class Meta:
        model = OrderAddress

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    city = "Abidjan"
    address_line = "Cocody Riviera 3"
    postal_code = "00225"


class DeliveryOptionFactory(DjangoModelFactory):
    class Meta:
        model = DeliveryOption

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Livraison {n}")
    description = "3–5 jours ouvrés"
    amount = Decimal("2500.00")
    currency = "XOF"
    position = factory.Sequence(lambda n: n)
    is_active = True
    is_default = False


class OrderPricingFactory(DjangoModelFactory):
    class Meta:
        model = OrderPricing

    order = factory.SubFactory(OrderFactory)
    delivery_option = factory.SubFactory(DeliveryOptionFactory)
    subtotal = Decimal("49.99")
    delivery_price = Decimal("2500.00")
    total = Decimal("2549.99")
    currency = "XOF"