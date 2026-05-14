"""
Tests d'intégration — SavedPrepaidCard + Health.
"""
import uuid

import pytest

from payement_app.models.prepay_cart import SavedPrepaidCard
from ..factories import SavedPrepaidCardFactory
from ..conftest import USER_ID, USER_ID_2

pytestmark = [pytest.mark.django_db, pytest.mark.integration]

BASE = "/payements/saved-cards"


class TestSavedCardListCreate:

    URL = f"{BASE}/"

    def test_list_requires_auth(self, api_client):
        resp = api_client.get(self.URL, {"user_id": str(USER_ID)})
        assert resp.status_code == 401

    def test_list_cards_for_user(self, auth_client):
        SavedPrepaidCardFactory(user_id=USER_ID)
        SavedPrepaidCardFactory(user_id=USER_ID)
        SavedPrepaidCardFactory(user_id=USER_ID_2)  # autre user
        resp = auth_client.get(self.URL, {"user_id": str(USER_ID)})
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_create_card(self, auth_client):
        data = {
            "user_id": str(USER_ID),
            "card_number": "4111111111111111",
            "card_holder": "Marie Koné",
            "expiration_date": "06/29",
            "cvv": "456",
        }
        resp = auth_client.post(self.URL, data, format="json")
        assert resp.status_code == 201
        assert resp.data["card_holder"] == "Marie Koné"
        assert resp.data["masked_card_number"] == "**** **** **** 1111"
        assert "card_number" not in resp.data
        assert "cvv" not in resp.data

    def test_create_requires_auth(self, api_client):
        data = {
            "user_id": str(USER_ID),
            "card_number": "4111111111111111",
            "card_holder": "Test",
            "expiration_date": "12/28",
            "cvv": "123",
        }
        resp = api_client.post(self.URL, data, format="json")
        assert resp.status_code == 401


class TestSavedCardDelete:

    def test_delete_card(self, auth_client, saved_card):
        url = f"{BASE}/{saved_card.id}/"
        resp = auth_client.delete(url)
        assert resp.status_code == 204
        assert not SavedPrepaidCard.objects.filter(pk=saved_card.id).exists()

    def test_delete_requires_auth(self, api_client, saved_card):
        url = f"{BASE}/{saved_card.id}/"
        resp = api_client.delete(url)
        assert resp.status_code == 401

    def test_delete_not_found(self, auth_client):
        url = f"{BASE}/{uuid.uuid4()}/"
        resp = auth_client.delete(url)
        assert resp.status_code == 404


class TestHealthCheck:

    def test_health_returns_ok(self, api_client):
        resp = api_client.get("/health/")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}