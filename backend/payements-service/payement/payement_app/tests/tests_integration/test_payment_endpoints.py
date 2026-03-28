# payement_app/tests/tests_integration/test_payment_endpoints.py
import uuid
import pytest
from decimal import Decimal
from payement_app.models.payment import Payment


PAYMENTS_URL = "/api/payments/"
PAYMENTS_LIST_URL = "/api/payments/list/"


def detail_url(transaction_reference):
    return f"/api/payments/{transaction_reference}/"


@pytest.mark.integration
@pytest.mark.django_db
class TestPaymentCreateEndpoint:

    def test_create_payment_returns_201(self, auth_client, valid_payment_payload):
        response = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert response.status_code == 201

    def test_create_payment_unauthenticated_returns_401(self, api_client, valid_payment_payload):
        response = api_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert response.status_code == 401

    def test_valid_card_creates_success_status(self, auth_client, valid_payment_payload):
        response = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert response.status_code == 201
        payment = Payment.objects.get(id=response.data["id"])
        assert payment.status == "success"

    def test_invalid_card_creates_failed_status(self, auth_client, invalid_card_payload):
        response = auth_client.post(PAYMENTS_URL, data=invalid_card_payload, format="json")
        assert response.status_code == 201
        payment = Payment.objects.get(id=response.data["id"])
        assert payment.status == "failed"

    def test_create_payment_persists_in_db(self, auth_client, valid_payment_payload):
        response = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert Payment.objects.filter(id=response.data["id"]).exists()

    def test_card_fields_not_in_response(self, auth_client, valid_payment_payload):
        response = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert "card_number" not in response.data
        assert "card_holder" not in response.data
        assert "cvv" not in response.data

    def test_transaction_reference_in_response(self, auth_client, valid_payment_payload):
        response = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert "transaction_reference" in response.data
        uuid.UUID(response.data["transaction_reference"])  # valide UUID

    def test_missing_card_number_returns_400(self, auth_client, valid_payment_payload):
        del valid_payment_payload["card_number"]
        response = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert response.status_code == 400

    def test_missing_order_pricing_id_returns_400(self, auth_client, valid_payment_payload):
        del valid_payment_payload["order_pricing_id"]
        response = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert response.status_code == 400

    def test_two_payments_have_different_transaction_references(self, auth_client, valid_payment_payload):
        r1 = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        valid_payment_payload["order_pricing_id"] = str(uuid.uuid4())
        r2 = auth_client.post(PAYMENTS_URL, data=valid_payment_payload, format="json")
        assert r1.data["transaction_reference"] != r2.data["transaction_reference"]


@pytest.mark.integration
@pytest.mark.django_db
class TestPaymentDetailEndpoint:

    def test_detail_returns_200(self, auth_client, payment):
        response = auth_client.get(detail_url(payment.transaction_reference))
        assert response.status_code == 200

    def test_detail_unauthenticated_returns_401(self, api_client, payment):
        response = api_client.get(detail_url(payment.transaction_reference))
        assert response.status_code == 401

    def test_detail_returns_correct_payment(self, auth_client, payment):
        response = auth_client.get(detail_url(payment.transaction_reference))
        assert response.data["id"] == str(payment.id)
        assert response.data["transaction_reference"] == str(payment.transaction_reference)

    def test_detail_nonexistent_returns_404(self, auth_client, db):
        response = auth_client.get(detail_url(uuid.uuid4()))
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestPaymentListEndpoint:

    def test_list_returns_200(self, auth_client, db):
        response = auth_client.get(PAYMENTS_LIST_URL)
        assert response.status_code == 200

    def test_list_unauthenticated_returns_401(self, api_client, db):
        response = api_client.get(PAYMENTS_LIST_URL)
        assert response.status_code == 401

    def test_list_filter_by_order_pricing_id(self, auth_client, db):
        target_id = uuid.uuid4()
        from payement_app.tests.factories import PaymentFactory
        PaymentFactory(order_pricing_id=target_id)
        PaymentFactory(order_pricing_id=target_id)
        PaymentFactory()  # autre commande

        response = auth_client.get(PAYMENTS_LIST_URL, {"order_pricing_id": str(target_id)})
        results = response.data["results"] if "results" in response.data else response.data
        assert len(results) == 2
        for p in results:
            assert p["order_pricing_id"] == str(target_id)

    def test_list_without_filter_returns_all(self, auth_client, db):
        from payement_app.tests.factories import PaymentFactory
        PaymentFactory.create_batch(3)
        response = auth_client.get(PAYMENTS_LIST_URL)
        count = response.data["count"] if "count" in response.data else len(response.data)
        assert count >= 3