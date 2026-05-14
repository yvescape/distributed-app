"""
Tests d'intégration — API Summary (produit).
"""
import pytest

from interation_app.models.like import Like
from interation_app.models.rating import Rating
from interation_app.tests.conftest import (
    PRODUCT_ID, USER_ID, USER_ID_2,
)


pytestmark = [pytest.mark.django_db, pytest.mark.integration]

BASE_URL = ""


class TestProductInteractionSummary:

    def test_summary_empty_product(self, api_client):
        """Produit sans interactions → tout à zéro."""
        url = f"{BASE_URL}/{PRODUCT_ID}/summary/"
        resp = api_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_likes"] == 0
        assert data["average_rating"] == 0
        assert data["total_ratings"] == 0
        assert data["liked"] is False

    def test_summary_with_likes_and_ratings(self, api_client):
        Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        Like.objects.create(user_id=USER_ID_2, product_id=PRODUCT_ID)
        Rating.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, value=4)
        Rating.objects.create(user_id=USER_ID_2, product_id=PRODUCT_ID, value=2)

        resp = api_client.get(f"{BASE_URL}/{PRODUCT_ID}/summary/")
        data = resp.json()
        assert data["total_likes"] == 2
        assert data["average_rating"] == 3.0
        assert data["total_ratings"] == 2

    def test_summary_accessible_without_auth(self, api_client):
        resp = api_client.get(f"{BASE_URL}/{PRODUCT_ID}/summary/")
        assert resp.status_code == 200

    def test_liked_false_for_anonymous_user(self, api_client):
        Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        resp = api_client.get(f"{BASE_URL}/{PRODUCT_ID}/summary/")
        assert resp.json()["liked"] is False

    def test_liked_true_for_authenticated_user_who_liked(self, auth_client):
        Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        resp = auth_client.get(f"{BASE_URL}/{PRODUCT_ID}/summary/")
        assert resp.json()["liked"] is True

    def test_liked_false_for_authenticated_user_who_did_not_like(self, auth_client_2):
        Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        resp = auth_client_2.get(f"{BASE_URL}/{PRODUCT_ID}/summary/")
        assert resp.json()["liked"] is False

    def test_average_rating_rounded_to_one_decimal(self, api_client):
        Rating.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, value=3)
        Rating.objects.create(user_id=USER_ID_2, product_id=PRODUCT_ID, value=5)
        # Moyenne = 4.0
        resp = api_client.get(f"{BASE_URL}/{PRODUCT_ID}/summary/")
        avg = resp.json()["average_rating"]
        # Vérifie que c'est arrondi à 1 décimale
        assert avg == round(avg, 1)