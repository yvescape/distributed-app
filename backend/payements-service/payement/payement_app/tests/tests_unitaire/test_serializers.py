"""
Tests unitaires — Serializers (Payment, SavedPrepaidCard).
"""
import uuid
from decimal import Decimal

import pytest

from payement_app.serializers.payment import PaymentSerializer
from payement_app.serializers.saved_prepaid_card import SavedPrepaidCardSerializer
from ..factories import PaymentFactory, SavedPrepaidCardFactory
from ..conftest import ORDER_PRICING_ID, ORDER_ID

pytestmark = [pytest.mark.django_db, pytest.mark.unit]


class TestPaymentSerializer:

    def test_valid_data(self):
        data = {
            "order_pricing_id": str(ORDER_PRICING_ID),
            "order_id": str(ORDER_ID),
            "amount": "15000",
            "currency": "FCFA",
            "card_number": "1234567890123456",
            "card_holder": "Jean Dupont",
            "expiration_date": "12/28",
            "cvv": "123",
        }
        s = PaymentSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_missing_card_number(self):
        data = {
            "order_pricing_id": str(ORDER_PRICING_ID),
            "order_id": str(ORDER_ID),
            "amount": "15000",
            "card_holder": "Jean",
            "expiration_date": "12/28",
            "cvv": "123",
        }
        s = PaymentSerializer(data=data)
        assert not s.is_valid()
        assert "card_number" in s.errors

    def test_missing_amount(self):
        data = {
            "order_pricing_id": str(ORDER_PRICING_ID),
            "order_id": str(ORDER_ID),
            "card_number": "1234567890123456",
            "card_holder": "Jean",
            "expiration_date": "12/28",
            "cvv": "123",
        }
        s = PaymentSerializer(data=data)
        assert not s.is_valid()
        assert "amount" in s.errors

    def test_write_only_fields_not_in_output(self):
        p = PaymentFactory()
        data = PaymentSerializer(p).data
        assert "card_number" not in data
        assert "card_holder" not in data
        assert "cvv" not in data
        assert "order_id" not in data

    def test_read_only_fields_in_output(self):
        p = PaymentFactory()
        data = PaymentSerializer(p).data
        assert "id" in data
        assert "status" in data
        assert "transaction_reference" in data
        assert "created_at" in data

    def test_create_success_with_valid_card(self):
        data = {
            "order_pricing_id": str(ORDER_PRICING_ID),
            "order_id": str(ORDER_ID),
            "amount": "15000",
            "currency": "FCFA",
            "card_number": "1234567890123456",
            "card_holder": "Jean",
            "expiration_date": "12/28",
            "cvv": "123",
        }
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        payment = s.save()
        assert payment.status == "success"

    def test_create_failed_with_invalid_card(self):
        data = {
            "order_pricing_id": str(ORDER_PRICING_ID),
            "order_id": str(ORDER_ID),
            "amount": "15000",
            "currency": "FCFA",
            "card_number": "INVALID",
            "card_holder": "Jean",
            "expiration_date": "12/28",
            "cvv": "123",
        }
        s = PaymentSerializer(data=data)
        assert s.is_valid()
        payment = s.save()
        assert payment.status == "failed"


class TestSavedPrepaidCardSerializer:

    def test_masked_card_number(self):
        card = SavedPrepaidCardFactory(card_number="4111111111111111")
        data = SavedPrepaidCardSerializer(card).data
        assert data["masked_card_number"] == "**** **** **** 1111"

    def test_card_number_write_only(self):
        card = SavedPrepaidCardFactory()
        data = SavedPrepaidCardSerializer(card).data
        assert "card_number" not in data

    def test_cvv_write_only(self):
        card = SavedPrepaidCardFactory()
        data = SavedPrepaidCardSerializer(card).data
        assert "cvv" not in data

    def test_valid_create_data(self):
        data = {
            "user_id": str(uuid.uuid4()),
            "card_number": "4111111111111111",
            "card_holder": "Marie Koné",
            "expiration_date": "06/29",
            "cvv": "456",
        }
        s = SavedPrepaidCardSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_output_contains_expected_fields(self):
        card = SavedPrepaidCardFactory()
        data = SavedPrepaidCardSerializer(card).data
        expected = {"id", "user_id", "card_holder", "masked_card_number", "expiration_date", "created_at"}
        assert set(data.keys()) == expected