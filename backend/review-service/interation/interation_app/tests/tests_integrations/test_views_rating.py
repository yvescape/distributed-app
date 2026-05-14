"""
Tests d'intégration — API Rating.
"""
import pytest

from interation_app.models.rating import Rating
from interation_app.tests.conftest import PRODUCT_ID, USER_ID


pytestmark = [pytest.mark.django_db, pytest.mark.integration]

BASE_URL = ""


class TestRatingCreateUpdate:

    def test_create_rating(self, auth_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/rating/"
        resp = auth_client.post(url, {"value": 4}, format="json")
        assert resp.status_code == 201
        assert Rating.objects.filter(user_id=USER_ID, product_id=PRODUCT_ID).exists()
        assert Rating.objects.get(user_id=USER_ID, product_id=PRODUCT_ID).value == 4

    def test_update_existing_rating(self, auth_client, mock_product_exists):
        """Un second POST met à jour la note existante (update_or_create)."""
        url = f"{BASE_URL}/{PRODUCT_ID}/rating/"
        auth_client.post(url, {"value": 3}, format="json")
        resp = auth_client.post(url, {"value": 5}, format="json")
        assert resp.status_code == 201
        assert Rating.objects.filter(user_id=USER_ID, product_id=PRODUCT_ID).count() == 1
        assert Rating.objects.get(user_id=USER_ID, product_id=PRODUCT_ID).value == 5

    def test_rating_requires_auth(self, api_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/rating/"
        resp = api_client.post(url, {"value": 4}, format="json")
        assert resp.status_code == 401

    def test_rating_product_not_found(self, auth_client, mock_product_not_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/rating/"
        resp = auth_client.post(url, {"value": 3}, format="json")
        assert resp.status_code == 400
        assert "product_id" in resp.json()

    @pytest.mark.parametrize("value", [0, -1, 6, 99])
    def test_invalid_rating_value(self, auth_client, mock_product_exists, value):
        url = f"{BASE_URL}/{PRODUCT_ID}/rating/"
        resp = auth_client.post(url, {"value": value}, format="json")
        assert resp.status_code == 400
        assert "value" in resp.json()

    def test_missing_value(self, auth_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/rating/"
        resp = auth_client.post(url, {}, format="json")
        assert resp.status_code == 400

    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5])
    def test_valid_boundary_values(self, auth_client, mock_product_exists, value):
        url = f"{BASE_URL}/{PRODUCT_ID}/rating/"
        resp = auth_client.post(url, {"value": value}, format="json")
        assert resp.status_code == 201