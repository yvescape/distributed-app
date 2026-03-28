# payement_app/tests/factories.py
import uuid
import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from payement_app.models.payment import Payment
from payement_app.models.prepay_cart import SavedPrepaidCard


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    id = factory.LazyFunction(uuid.uuid4)
    order_pricing_id = factory.LazyFunction(uuid.uuid4)
    amount = Decimal("2500")
    currency = "XOF"
    status = "success"
    transaction_reference = factory.LazyFunction(uuid.uuid4)


class SavedPrepaidCardFactory(DjangoModelFactory):
    class Meta:
        model = SavedPrepaidCard

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    card_number = "1234567890123456"
    card_holder = factory.Faker("name")
    expiration_date = "12/27"
    cvv = "123"