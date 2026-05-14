"""
Factories pour les tests du payment-service.
"""
import uuid
from decimal import Decimal
import factory
from factory.django import DjangoModelFactory
from payement_app.models.payment import Payment
from payement_app.models.prepay_cart import SavedPrepaidCard


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    id = factory.LazyFunction(uuid.uuid4)
    order_pricing_id = factory.LazyFunction(uuid.uuid4)
    amount = Decimal("15000")
    currency = "FCFA"
    status = "success"
    transaction_reference = factory.LazyFunction(uuid.uuid4)


class SavedPrepaidCardFactory(DjangoModelFactory):
    class Meta:
        model = SavedPrepaidCard

    id = factory.LazyFunction(uuid.uuid4)
    user_id = factory.LazyFunction(uuid.uuid4)
    card_number = "4111111111111111"
    card_holder = "Jean Dupont"
    expiration_date = "12/28"
    cvv = "123"