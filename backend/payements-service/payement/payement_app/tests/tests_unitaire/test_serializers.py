# payement_app/tests/tests_unitaire/test_serializers.py
import uuid
import pytest
from decimal import Decimal
from payement_app.serializers.payment import PaymentSerializer
from payement_app.serializers.saved_prepaid_card import SavedPrepaidCardSerializer
from payement_app.models.payment import Payment
from ..factories import PaymentFactory, SavedPrepaidCardFactory


def _valid_payment_data():
    return {
        "order_pricing_id": str(uuid.uuid4()),
        "amount": "2500",
        "currency": "XOF",
        "card_number": "1234567890123456",
        "card_holder": "Kouadio Jean",
        "expiration_date": "12/27",
        "cvv": "123",
    }


@pytest.mark.unit
class TestPaymentSerializer:

    def test_valid_data_accepted(self, db):
        s = PaymentSerializer(data=_valid_payment_data())
        assert s.is_valid(), s.errors

    def test_valid_card_creates_success_payment(self, db):
        s = PaymentSerializer(data=_valid_payment_data())
        assert s.is_valid()
        payment = s.save()
        assert payment.status == "success"

    def test_invalid_card_creates_failed_payment(self, db):
        data = _valid_payment_data()
        data["card_number"] = "1234-5678-9012-3456"
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        payment = s.save()
        assert payment.status == "failed"

    def test_card_with_letters_creates_failed_payment(self, db):
        data = _valid_payment_data()
        data["card_number"] = "123456789012345X"
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        payment = s.save()
        assert payment.status == "failed"

    def test_card_too_short_creates_failed_payment(self, db):
        data = _valid_payment_data()
        data["card_number"] = "123456789"
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        payment = s.save()
        assert payment.status == "failed"

    def test_card_fields_are_write_only(self, db):
        payment = PaymentFactory()
        data = PaymentSerializer(payment).data
        assert "card_number" not in data
        assert "card_holder" not in data
        assert "expiration_date" not in data
        assert "cvv" not in data

    def test_status_is_read_only(self, db):
        data = _valid_payment_data()
        data["status"] = "success"
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        assert "status" not in s.validated_data

    def test_transaction_reference_is_read_only(self, db):
        data = _valid_payment_data()
        data["transaction_reference"] = str(uuid.uuid4())
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        assert "transaction_reference" not in s.validated_data

    def test_id_is_read_only(self, db):
        data = _valid_payment_data()
        data["id"] = str(uuid.uuid4())
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        assert "id" not in s.validated_data

    def test_expected_output_fields(self, db):
        payment = PaymentFactory()
        data = PaymentSerializer(payment).data
        expected = {"id", "order_pricing_id", "amount", "currency",
                    "status", "transaction_reference", "created_at"}
        assert set(data.keys()) == expected

    def test_missing_order_pricing_id_rejected(self, db):
        data = _valid_payment_data()
        del data["order_pricing_id"]
        s = PaymentSerializer(data=data)
        assert not s.is_valid()
        assert "order_pricing_id" in s.errors

    def test_missing_card_number_rejected(self, db):
        data = _valid_payment_data()
        del data["card_number"]
        s = PaymentSerializer(data=data)
        assert not s.is_valid()
        assert "card_number" in s.errors

    def test_transaction_reference_unique_per_payment(self, db):
        s1 = PaymentSerializer(data=_valid_payment_data())
        s2 = PaymentSerializer(data=_valid_payment_data())
        assert s1.is_valid()
        assert s2.is_valid()
        p1 = s1.save()
        p2 = s2.save()
        assert p1.transaction_reference != p2.transaction_reference


@pytest.mark.unit
class TestSavedPrepaidCardSerializer:

    def test_valid_data_accepted(self, db):
        data = {
            "user_id": str(uuid.uuid4()),
            "card_number": "1234567890123456",
            "card_holder": "Kouadio Jean",
            "expiration_date": "12/27",
            "cvv": "123",
        }
        s = SavedPrepaidCardSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_masked_card_number_shows_last_four(self, db):
        card = SavedPrepaidCardFactory(card_number="1234567890123456")
        data = SavedPrepaidCardSerializer(card).data
        assert data["masked_card_number"] == "**** **** **** 3456"

    def test_card_number_not_exposed_in_output(self, db):
        """card_number est write_only — ne doit pas apparaître en sortie."""
        card = SavedPrepaidCardFactory(card_number="1234567890123456")
        data = SavedPrepaidCardSerializer(card).data
        assert "card_number" not in data
        assert "cvv" not in data

    def test_expected_fields(self, db):
        card = SavedPrepaidCardFactory()
        data = SavedPrepaidCardSerializer(card).data
        # card_number et cvv sont write_only — absents de l'output
        expected = {"id", "user_id", "card_holder", "masked_card_number",
                    "expiration_date", "created_at"}
        assert set(data.keys()) == expected

    def test_id_is_read_only(self, db):
        data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "card_number": "1234567890123456",
            "card_holder": "Test",
            "expiration_date": "12/27",
            "cvv": "123",
        }
        s = SavedPrepaidCardSerializer(data=data)
        assert s.is_valid()
        assert "id" not in s.validated_data