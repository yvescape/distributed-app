"""
Factories pour les tests du orders-service.
"""
import uuid
from decimal import Decimal
import factory
from factory.django import DjangoModelFactory
from orders_app.models.order import Order
from orders_app.models.order_item import OrderItem
from orders_app.models.order_address import OrderAddress
from orders_app.models.order_pricing import OrderPricing
from orders_app.models.delivery_option import DeliveryOption


class DeliveryOptionFactory(DjangoModelFactory):
    class Meta:
        model = DeliveryOption

    id = factory.LazyFunction(uuid.uuid4)
    name = "Livraison standard"
    description = "3-5 jours ouvrés"
    amount = Decimal("2000.00")
    currency = "XOF"
    position = 0
    is_active = True
    is_default = True


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    session_id = None
    status = "pending"


class GuestOrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    id = factory.LazyFunction(uuid.uuid4)
    user_id = None
    session_id = factory.LazyFunction(uuid.uuid4)
    status = "pending"


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    product_id = factory.LazyFunction(uuid.uuid4)
    product_name = factory.Sequence(lambda n: f"Parfum Test {n}")
    product_image = "https://cdn.example.com/image.jpg"
    product_size = "100ml"
    price = Decimal("50.00")
    quantity = 1
    total = Decimal("50.00")


class OrderAddressFactory(DjangoModelFactory):
    class Meta:
        model = OrderAddress

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    first_name = "Jean"
    last_name = "Dupont"
    email = "jean@example.com"
    mobile = "+2250101010101"
    city = "Abidjan"
    address_line = "Cocody, Rue des Jardins"


class OrderPricingFactory(DjangoModelFactory):
    class Meta:
        model = OrderPricing

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    delivery_option = factory.SubFactory(DeliveryOptionFactory)
    subtotal = Decimal("50.00")
    delivery_price = Decimal("2000.00")
    total = Decimal("2050.00")
    currency = "FCFA"