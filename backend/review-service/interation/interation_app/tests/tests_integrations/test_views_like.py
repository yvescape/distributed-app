"""
Tests d'intégration — API Toggle Like.
"""
import pytest

from interation_app.models.like import Like
from interation_app.tests.conftest import PRODUCT_ID, USER_ID


pytestmark = [pytest.mark.django_db, pytest.mark.integration]

BASE_URL = ""

class TestToggleLike:

    def test_like_product(self, auth_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/toggle-like/"
        resp = auth_client.post(url)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Product liked"
        assert Like.objects.filter(user_id=USER_ID, product_id=PRODUCT_ID).exists()

    def test_unlike_product(self, auth_client, mock_product_exists):
        Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        url = f"{BASE_URL}/{PRODUCT_ID}/toggle-like/"
        resp = auth_client.post(url)
        assert resp.status_code == 200
        assert resp.json()["message"] == "Like removed"
        assert not Like.objects.filter(user_id=USER_ID, product_id=PRODUCT_ID).exists()

    def test_toggle_twice_returns_to_liked(self, auth_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/toggle-like/"
        auth_client.post(url)  # like
        auth_client.post(url)  # unlike
        resp = auth_client.post(url)  # like again
        assert resp.json()["message"] == "Product liked"
        assert Like.objects.filter(user_id=USER_ID, product_id=PRODUCT_ID).count() == 1

    def test_like_requires_auth(self, api_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/toggle-like/"
        resp = api_client.post(url)
        assert resp.status_code == 401

    def test_like_product_not_found(self, auth_client, mock_product_not_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/toggle-like/"
        resp = auth_client.post(url)
        assert resp.status_code == 400
        assert "product_id" in resp.json()