# payement_app/tests/tests_unitaire/test_models.py
import uuid
import pytest
from decimal import Decimal
from django.utils import timezone
from payement_app.models.payment import Payment
from payement_app.models.prepay_cart import SavedPrepaidCard
from ..factories import PaymentFactory, SavedPrepaidCardFactory


@pytest.mark.unit
class TestPaymentModel:

    def test_payment_creation(self, db):
        payment = PaymentFactory()
        assert payment.pk is not None
        assert isinstance(payment.id, uuid.UUID)

    def test_payment_str(self, db):
        payment = PaymentFactory(status="success")
        assert str(payment) == f"Payment {payment.order_pricing_id} - success"

    def test_payment_id_is_uuid(self, db):
        payment = PaymentFactory()
        assert isinstance(payment.id, uuid.UUID)

    def test_payment_transaction_reference_is_uuid(self, db):
        payment = PaymentFactory()
        assert isinstance(payment.transaction_reference, uuid.UUID)

    def test_payment_transaction_reference_is_unique(self, db):
        from django.db import IntegrityError
        ref = uuid.uuid4()
        PaymentFactory(transaction_reference=ref)
        with pytest.raises(IntegrityError):
            PaymentFactory(transaction_reference=ref)

    def test_payment_default_currency_xof(self, db):
        payment = PaymentFactory()
        assert payment.currency == "XOF"

    def test_payment_status_choices(self, db):
        for status in ["success", "failed"]:
            p = PaymentFactory(status=status)
            assert p.status == status

    def test_payment_order_pricing_id_is_uuid(self, db):
        payment = PaymentFactory()
        assert isinstance(payment.order_pricing_id, uuid.UUID)

    def test_payment_timestamp_set_on_creation(self, db):
        before = timezone.now()
        payment = PaymentFactory()
        after = timezone.now()
        assert before <= payment.created_at <= after

    def test_payment_amount_precision(self, db):
        payment = PaymentFactory(amount=Decimal("2500"))
        payment.refresh_from_db()
        assert payment.amount == Decimal("2500")


@pytest.mark.unit
class TestSavedPrepaidCardModel:

    def test_card_creation(self, db):
        card = SavedPrepaidCardFactory()
        assert card.pk is not None
        assert isinstance(card.id, uuid.UUID)

    def test_card_str_shows_last_four_digits(self, db):
        card = SavedPrepaidCardFactory(
            card_holder="Jean Kouadio",
            card_number="1234567890123456"
        )
        assert str(card) == "Jean Kouadio - 3456"

    def test_card_user_id_is_uuid(self, db):
        card = SavedPrepaidCardFactory()
        assert isinstance(card.user_id, uuid.UUID)

    def test_card_timestamp_set_on_creation(self, db):
        before = timezone.now()
        card = SavedPrepaidCardFactory()
        after = timezone.now()
        assert before <= card.created_at <= after

    def test_multiple_cards_per_user(self, db):
        user_id = uuid.uuid4()
        SavedPrepaidCardFactory(user_id=user_id, card_number="1111222233334444")
        SavedPrepaidCardFactory(user_id=user_id, card_number="5555666677778888")
        assert SavedPrepaidCard.objects.filter(user_id=user_id).count() == 2