# products_app/tests/tests_integration/test_product_endpoints.py
import pytest
import uuid
from decimal import Decimal
from ..factories import ProductFactory


PRODUCTS_URL = "/api/products/"


def detail_url(product_id):
    return f"/api/products/{product_id}/"


@pytest.mark.integration
@pytest.mark.django_db
class TestProductListEndpoint:

    def test_list_returns_200(self, api_client, db):
        response = api_client.get(PRODUCTS_URL)
        assert response.status_code == 200

    def test_list_accessible_without_auth(self, api_client, db):
        """Les produits sont publics — aucune auth requise."""
        response = api_client.get(PRODUCTS_URL)
        assert response.status_code == 200

    def test_list_returns_paginated_response(self, api_client, db):
        ProductFactory.create_batch(3)
        response = api_client.get(PRODUCTS_URL)
        assert "results" in response.data
        assert "count" in response.data

    def test_list_count_correct(self, api_client, db):
        ProductFactory.create_batch(4)
        response = api_client.get(PRODUCTS_URL)
        assert response.data["count"] == 4

    def test_list_empty_when_no_products(self, api_client, db):
        response = api_client.get(PRODUCTS_URL)
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_list_ordered_by_created_at_desc(self, api_client, db):
        products = ProductFactory.create_batch(3)
        response = api_client.get(PRODUCTS_URL)
        names = [p["name"] for p in response.data["results"]]
        # Le plus récent doit apparaître en premier
        assert names.index(products[-1].name) < names.index(products[0].name)

    def test_list_uses_card_serializer_fields(self, api_client, db):
        ProductFactory()
        response = api_client.get(PRODUCTS_URL)
        product = response.data["results"][0]
        expected = {"id", "name", "category", "price", "size", "image", "notes", "badge"}
        assert expected.issubset(set(product.keys()))

    def test_list_does_not_expose_detail_fields(self, api_client, db):
        """La liste ne doit pas exposer les champs détail."""
        ProductFactory()
        response = api_client.get(PRODUCTS_URL)
        product = response.data["results"][0]
        hidden = {"notes_top", "notes_heart", "notes_base", "composition", "advice"}
        assert not hidden.intersection(set(product.keys()))

    def test_list_notes_combined_correctly(self, api_client, db):
        ProductFactory(notes_top="Bergamote", notes_heart="Jasmin", notes_base="Musc")
        response = api_client.get(PRODUCTS_URL)
        product = response.data["results"][0]
        assert product["notes"] == "Bergamote · Jasmin · Musc"


@pytest.mark.integration
@pytest.mark.django_db
class TestProductDetailEndpoint:

    def test_detail_returns_200(self, api_client, product):
        response = api_client.get(detail_url(product.id))
        assert response.status_code == 200

    def test_detail_accessible_without_auth(self, api_client, product):
        response = api_client.get(detail_url(product.id))
        assert response.status_code == 200

    def test_detail_returns_correct_product(self, api_client, product):
        response = api_client.get(detail_url(product.id))
        assert response.data["id"] == str(product.id)
        assert response.data["name"] == product.name

    def test_detail_contains_all_fields(self, api_client, product):
        response = api_client.get(detail_url(product.id))
        expected = {
            "id", "name", "category", "price", "size", "image", "badge",
            "family", "gender", "notes_top", "notes_heart", "notes_base",
            "composition", "advice", "created_at", "updated_at",
        }
        assert expected.issubset(set(response.data.keys()))

    def test_detail_notes_fields_separate(self, api_client, db):
        product = ProductFactory(
            notes_top="Bergamote",
            notes_heart="Jasmin",
            notes_base="Musc blanc",
        )
        response = api_client.get(detail_url(product.id))
        assert response.data["notes_top"] == "Bergamote"
        assert response.data["notes_heart"] == "Jasmin"
        assert response.data["notes_base"] == "Musc blanc"

    def test_detail_nonexistent_returns_404(self, api_client, db):
        response = api_client.get(detail_url(uuid.uuid4()))
        assert response.status_code == 404

    def test_detail_invalid_uuid_returns_404(self, api_client, db):
        response = api_client.get("/api/products/not-a-uuid/")
        assert response.status_code == 404

    def test_detail_price_value(self, api_client, db):
        product = ProductFactory(price=Decimal("149.99"))
        response = api_client.get(detail_url(product.id))
        assert response.data["price"] == "149.99"

    def test_detail_badge_null_when_not_set(self, api_client, db):
        product = ProductFactory(badge=None)
        response = api_client.get(detail_url(product.id))
        assert response.data["badge"] is None


@pytest.mark.integration
@pytest.mark.django_db
class TestHealthEndpoint:

    def test_health_returns_200(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == 200

    def test_health_returns_ok(self, api_client):
        response = api_client.get("/health/")
        assert response.json() == {"status": "ok"}

    def test_health_no_auth_required(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == 200