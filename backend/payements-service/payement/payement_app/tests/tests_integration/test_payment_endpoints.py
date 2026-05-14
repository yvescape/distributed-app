"""
Tests d'intégration — Payment endpoints (create, list, detail).
"""
import uuid
from decimal import Decimal

import pytest

from payement_app.models.payment import Payment
from ..factories import PaymentFactory
from ..conftest import USER_ID, ORDER_PRICING_ID

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

BASE = "/payements"


class TestPaymentCreate:

    URL = f"{BASE}/create/"

    def test_create_success_with_valid_card(self, api_client, valid_payment_payload, mock_order_confirm_success):
        resp = api_client.post(self.URL, valid_payment_payload, format="json")
        assert resp.status_code == 201
        assert resp.data["status"] == "success"
        assert Payment.objects.count() == 1

    def test_create_failed_with_invalid_card(self, api_client, invalid_card_payload):
        resp = api_client.post(self.URL, invalid_card_payload, format="json")
        assert resp.status_code == 201
        assert resp.data["status"] == "failed"

    def test_create_success_calls_order_confirm(self, api_client, valid_payment_payload, mock_order_confirm_success):
        api_client.post(self.URL, valid_payment_payload, format="json")
        mock_order_confirm_success.assert_called_once()

    def test_create_failed_does_not_call_order_confirm(self, api_client, invalid_card_payload, mock_order_confirm_success):
        api_client.post(self.URL, invalid_card_payload, format="json")
        mock_order_confirm_success.assert_not_called()

    def test_create_order_confirm_failure_marks_payment_failed(self, api_client, valid_payment_payload, mock_order_confirm_failure):
        with pytest.raises(Exception, match="Order confirmation failed"):
            api_client.post(self.URL, valid_payment_payload, format="json")
        payment = Payment.objects.first()
        assert payment.status == "failed"

    def test_create_missing_fields(self, api_client):
        resp = api_client.post(self.URL, {}, format="json")
        assert resp.status_code == 400

    def test_create_returns_transaction_reference(self, api_client, valid_payment_payload, mock_order_confirm_success):
        resp = api_client.post(self.URL, valid_payment_payload, format="json")
        assert resp.status_code == 201
        assert "transaction_reference" in resp.data

    def test_card_fields_not_in_response(self, api_client, valid_payment_payload, mock_order_confirm_success):
        resp = api_client.post(self.URL, valid_payment_payload, format="json")
        assert "card_number" not in resp.data
        assert "cvv" not in resp.data


class TestPaymentList:

    URL = f"{BASE}/list/"

    def test_list_requires_auth(self, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 401

    def test_list_returns_payments(self, auth_client):
        PaymentFactory.create_batch(3)
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        assert len(resp.data) == 3

    def test_list_filter_by_order_pricing_id(self, auth_client):
        PaymentFactory(order_pricing_id=ORDER_PRICING_ID)
        PaymentFactory()  # autre order
        resp = auth_client.get(self.URL, {"order_pricing_id": str(ORDER_PRICING_ID)})
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_list_empty(self, auth_client):
        resp = auth_client.get(self.URL)
        assert resp.status_code == 200
        assert resp.data == []


class TestPaymentDetail:

    def test_detail_by_transaction_reference(self, auth_client, payment):
        url = f"{BASE}/{payment.transaction_reference}/"
        resp = auth_client.get(url)
        assert resp.status_code == 200
        assert resp.data["id"] == str(payment.id)

    def test_detail_requires_auth(self, api_client, payment):
        url = f"{BASE}/{payment.transaction_reference}/"
        resp = api_client.get(url)
        assert resp.status_code == 401

    def test_detail_not_found(self, auth_client):
        url = f"{BASE}/{uuid.uuid4()}/"
        resp = auth_client.get(url)
        assert resp.status_code == 404