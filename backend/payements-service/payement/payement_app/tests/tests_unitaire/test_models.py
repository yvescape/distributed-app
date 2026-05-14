"""
Tests unitaires — Modèles (Payment, SavedPrepaidCard).
"""
import uuid
from decimal import Decimal

import pytest

from payement_app.models.payment import Payment
from payement_app.models.prepay_cart import SavedPrepaidCard
from ..factories import PaymentFactory, SavedPrepaidCardFactory

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


class TestPaymentModel:

    def test_create_payment(self):
        p = PaymentFactory()
        assert p.pk is not None
        assert p.status == "success"
        assert p.currency == "FCFA"

    def test_str(self):
        p = PaymentFactory(status="failed")
        assert "failed" in str(p)

    def test_transaction_reference_is_uuid(self):
        p = PaymentFactory()
        assert isinstance(p.transaction_reference, uuid.UUID)

    def test_transaction_reference_unique(self):
        ref = uuid.uuid4()
        PaymentFactory(transaction_reference=ref)
        with pytest.raises(Exception):
            PaymentFactory(transaction_reference=ref)

    def test_amount_decimal(self):
        p = PaymentFactory(amount=Decimal("25000"))
        assert p.amount == Decimal("25000")


class TestSavedPrepaidCardModel:

    def test_create_card(self):
        card = SavedPrepaidCardFactory()
        assert card.pk is not None
        assert card.card_holder == "Jean Dupont"

    def test_str_shows_last_4_digits(self):
        card = SavedPrepaidCardFactory(card_number="4111111111111111", card_holder="Marie")
        s = str(card)
        assert "Marie" in s
        assert "1111" in s

    def test_card_number_stored_full(self):
        card = SavedPrepaidCardFactory(card_number="9876543210123456")
        assert card.card_number == "9876543210123456"