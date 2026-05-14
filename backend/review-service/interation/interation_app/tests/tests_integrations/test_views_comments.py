"""
Tests d'intégration — API Comments.
"""
import uuid

import pytest

from interation_app.models.comment import Comment
from interation_app.tests.conftest import (
    PRODUCT_ID, PRODUCT_ID_2, USER_ID, USER_ID_2, USER_EMAIL, USER_EMAIL_2,
)


pytestmark = [pytest.mark.django_db, pytest.mark.integration]

BASE_URL = ""


# ═══════════════════════════════════════════════════════════════════════
#  GET  /<product_id>/comments/   (liste publique)
# ═══════════════════════════════════════════════════════════════════════

class TestCommentList:

    def test_list_empty(self, api_client):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/"
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_comments_for_product(self, api_client):
        Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="Bon", user_email=USER_EMAIL)
        Comment.objects.create(user_id=USER_ID_2, product_id=PRODUCT_ID, content="Très bon", user_email=USER_EMAIL_2)
        # Commentaire sur un AUTRE produit → ne doit pas apparaître
        Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID_2, content="Autre produit")

        resp = api_client.get(f"{BASE_URL}/{PRODUCT_ID}/comments/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        # Trié par created_at desc
        assert data[0]["content"] == "Très bon"

    def test_list_accessible_without_auth(self, api_client):
        resp = api_client.get(f"{BASE_URL}/{PRODUCT_ID}/comments/")
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
#  POST  /<product_id>/comments/create/   (auth requise)
# ═══════════════════════════════════════════════════════════════════════

class TestCommentCreate:

    def test_create_success(self, auth_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/create/"
        resp = auth_client.post(url, {"content": "Super !"}, format="json")
        assert resp.status_code == 201
        assert resp.json()["content"] == "Super !"
        assert resp.json()["user_email"] == USER_EMAIL
        assert resp.json()["product_id"] == str(PRODUCT_ID)

    def test_create_requires_auth(self, api_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/create/"
        resp = api_client.post(url, {"content": "Nope"}, format="json")
        assert resp.status_code == 401

    def test_create_product_not_found(self, auth_client, mock_product_not_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/create/"
        resp = auth_client.post(url, {"content": "Test"}, format="json")
        assert resp.status_code == 400
        assert "product_id" in resp.json()

    def test_create_duplicate_blocked(self, auth_client, mock_product_exists):
        Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="Déjà là")
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/create/"
        resp = auth_client.post(url, {"content": "Doublon"}, format="json")
        assert resp.status_code == 400
        assert "déjà commenté" in str(resp.json()).lower()

    def test_create_empty_content(self, auth_client, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/create/"
        resp = auth_client.post(url, {"content": ""}, format="json")
        assert resp.status_code == 400

    def test_two_users_can_comment_same_product(self, auth_client, auth_client_2, mock_product_exists):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/create/"
        r1 = auth_client.post(url, {"content": "User 1"}, format="json")
        r2 = auth_client_2.post(url, {"content": "User 2"}, format="json")
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert Comment.objects.filter(product_id=PRODUCT_ID).count() == 2


# ═══════════════════════════════════════════════════════════════════════
#  PATCH  /<product_id>/comments/update/   (auth requise)
# ═══════════════════════════════════════════════════════════════════════

class TestCommentUpdate:

    def test_update_own_comment(self, auth_client):
        Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="Ancien")
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/update/"
        resp = auth_client.patch(url, {"content": "Modifié"}, format="json")
        assert resp.status_code == 200
        assert resp.json()["content"] == "Modifié"

    def test_update_no_comment_exists(self, auth_client):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/update/"
        resp = auth_client.patch(url, {"content": "???"}, format="json")
        assert resp.status_code == 400
        assert "aucun commentaire" in str(resp.json()).lower()

    def test_update_requires_auth(self, api_client):
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/update/"
        resp = api_client.patch(url, {"content": "Nope"}, format="json")
        assert resp.status_code == 401

    def test_cannot_update_other_users_comment(self, auth_client_2):
        """User 2 ne peut pas modifier le commentaire de User 1."""
        Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="User 1")
        url = f"{BASE_URL}/{PRODUCT_ID}/comments/update/"
        resp = auth_client_2.patch(url, {"content": "Hacked"}, format="json")
        assert resp.status_code == 400  # Pas de commentaire trouvé pour user 2