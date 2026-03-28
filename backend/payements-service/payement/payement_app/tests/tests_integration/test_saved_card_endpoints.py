# payement_app/tests/tests_integration/test_saved_card_endpoints.py
import uuid
import pytest
from payement_app.models.prepay_cart import SavedPrepaidCard
from payement_app.tests.factories import SavedPrepaidCardFactory


SAVED_CARDS_URL = "/api/saved-cards/"


def delete_url(pk):
    return f"/api/saved-cards/{pk}/"


@pytest.mark.integration
@pytest.mark.django_db
class TestSavedPrepaidCardListCreateEndpoint:

    def test_list_returns_200(self, auth_client, user_id, db):
        response = auth_client.get(SAVED_CARDS_URL, {"user_id": str(user_id)})
        assert response.status_code == 200

    def test_list_unauthenticated_returns_401(self, api_client, user_id, db):
        response = api_client.get(SAVED_CARDS_URL, {"user_id": str(user_id)})
        assert response.status_code == 401

    def test_list_filters_by_user_id(self, auth_client, user_id, db):
        SavedPrepaidCardFactory(user_id=user_id)
        SavedPrepaidCardFactory(user_id=user_id)
        SavedPrepaidCardFactory()  # autre utilisateur

        response = auth_client.get(SAVED_CARDS_URL, {"user_id": str(user_id)})
        results = response.data["results"] if "results" in response.data else response.data
        assert len(results) == 2

    def test_create_card_returns_201(self, auth_client, user_id):
        data = {
            "user_id": str(user_id),
            "card_number": "1234567890123456",
            "card_holder": "Kouadio Jean",
            "expiration_date": "12/27",
            "cvv": "123",
        }
        response = auth_client.post(SAVED_CARDS_URL, data=data, format="json")
        assert response.status_code == 201

    def test_create_card_unauthenticated_returns_401(self, api_client, user_id):
        data = {
            "user_id": str(user_id),
            "card_number": "1234567890123456",
            "card_holder": "Kouadio Jean",
            "expiration_date": "12/27",
            "cvv": "123",
        }
        response = api_client.post(SAVED_CARDS_URL, data=data, format="json")
        assert response.status_code == 401

    def test_create_card_persists_in_db(self, auth_client, user_id):
        data = {
            "user_id": str(user_id),
            "card_number": "1234567890123456",
            "card_holder": "Kouadio Jean",
            "expiration_date": "12/27",
            "cvv": "123",
        }
        auth_client.post(SAVED_CARDS_URL, data=data, format="json")
        assert SavedPrepaidCard.objects.filter(user_id=user_id).exists()

    def test_create_card_returns_masked_number(self, auth_client, user_id):
        data = {
            "user_id": str(user_id),
            "card_number": "1234567890123456",
            "card_holder": "Kouadio Jean",
            "expiration_date": "12/27",
            "cvv": "123",
        }
        response = auth_client.post(SAVED_CARDS_URL, data=data, format="json")
        assert response.data["masked_card_number"] == "**** **** **** 3456"


@pytest.mark.integration
@pytest.mark.django_db
class TestSavedPrepaidCardDeleteEndpoint:

    def test_delete_returns_204(self, auth_client, saved_card):
        response = auth_client.delete(delete_url(saved_card.id))
        assert response.status_code == 204

    def test_delete_unauthenticated_returns_401(self, api_client, saved_card):
        response = api_client.delete(delete_url(saved_card.id))
        assert response.status_code == 401

    def test_delete_removes_from_db(self, auth_client, saved_card):
        card_id = saved_card.id
        auth_client.delete(delete_url(card_id))
        assert not SavedPrepaidCard.objects.filter(id=card_id).exists()

    def test_delete_nonexistent_returns_404(self, auth_client, db):
        response = auth_client.delete(delete_url(uuid.uuid4()))
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestHealthEndpoint:

    def test_health_returns_200(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == 200

    def test_health_returns_ok(self, api_client):
        assert api_client.get("/health/").json() == {"status": "ok"}

    def test_health_no_auth_required(self, api_client):
        assert api_client.get("/health/").status_code == 200