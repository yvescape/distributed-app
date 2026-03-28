# orders_app/tests/tests_integration/test_delivery_endpoints.py
import pytest
import uuid
from decimal import Decimal
from rest_framework.test import APIClient
from orders_app.models.delivery_option import DeliveryOption
from ..factories import DeliveryOptionFactory


DELIVERY_URL = "/api/delivery/"


def detail_url(pk):
    return f"/api/delivery/{pk}/"


def update_url(pk):
    return f"/api/delivery/{pk}/update/"


def delete_url(pk):
    return f"/api/delivery/{pk}/delete/"


CREATE_URL = "/api/delivery/create/"


def _make_admin_client():
    """Client simulant un admin via force_authenticate."""
    from django.contrib.auth.models import User
    from rest_framework.test import APIClient
    client = APIClient()
    # Dans un microservice sans modèle User local, on mock l'admin
    admin = type("FakeAdmin", (), {"id": uuid.uuid4(), "is_staff": True,
                                   "is_superuser": True, "is_active": True,
                                   "is_authenticated": True, "pk": 1})()
    client.force_authenticate(user=admin)
    return client


@pytest.mark.integration
@pytest.mark.django_db
class TestDeliveryOptionListEndpoint:

    def test_list_returns_200(self, api_client, db):
        DeliveryOptionFactory.create_batch(3, is_active=True)
        response = api_client.get(DELIVERY_URL)
        assert response.status_code == 200

    def test_list_no_auth_required(self, api_client, db):
        response = api_client.get(DELIVERY_URL)
        assert response.status_code == 200

    def test_list_only_active_options(self, api_client, db):
        DeliveryOptionFactory.create_batch(2, is_active=True)
        DeliveryOptionFactory.create_batch(3, is_active=False)
        response = api_client.get(DELIVERY_URL)
        results = response.data["results"] if "results" in response.data else response.data
        for opt in results:
            assert opt["is_active"] is True

    def test_list_ordered_by_position(self, api_client, db):
        DeliveryOptionFactory(position=2, is_active=True)
        DeliveryOptionFactory(position=0, is_active=True)
        DeliveryOptionFactory(position=1, is_active=True)
        response = api_client.get(DELIVERY_URL)
        results = response.data["results"] if "results" in response.data else response.data
        positions = [opt["position"] for opt in results]
        assert positions == sorted(positions)

    def test_list_contains_expected_fields(self, api_client, db):
        DeliveryOptionFactory(is_active=True)
        response = api_client.get(DELIVERY_URL)
        results = response.data["results"] if "results" in response.data else response.data
        opt = results[0]
        expected = {"id", "name", "description", "amount", "currency", "position", "is_default", "is_active", "created_at"}
        assert expected.issubset(set(opt.keys()))


@pytest.mark.integration
@pytest.mark.django_db
class TestDeliveryOptionDetailEndpoint:

    def test_detail_returns_200(self, api_client, delivery_option):
        response = api_client.get(detail_url(delivery_option.id))
        assert response.status_code == 200

    def test_detail_correct_data(self, api_client, delivery_option):
        response = api_client.get(detail_url(delivery_option.id))
        assert response.data["id"] == str(delivery_option.id)
        assert response.data["name"] == delivery_option.name

    def test_detail_inactive_returns_404(self, api_client, db):
        inactive = DeliveryOptionFactory(is_active=False)
        response = api_client.get(detail_url(inactive.id))
        assert response.status_code == 404

    def test_detail_nonexistent_returns_404(self, api_client, db):
        response = api_client.get(detail_url(uuid.uuid4()))
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestDeliveryOptionAdminEndpoints:

    def test_create_requires_admin(self, api_client):
        data = {"name": "Express", "description": "24h", "amount": "5000", "currency": "XOF", "position": 0, "is_default": False, "is_active": True}
        response = api_client.post(CREATE_URL, data=data, format="json")
        assert response.status_code in (401, 403)

    def test_update_requires_admin(self, api_client, delivery_option):
        response = api_client.patch(update_url(delivery_option.id), data={"name": "Updated"}, format="json")
        assert response.status_code in (401, 403)

    def test_delete_requires_admin(self, api_client, delivery_option):
        response = api_client.delete(delete_url(delivery_option.id))
        assert response.status_code in (401, 403)

    def test_admin_can_create_delivery_option(self, db):
        client = _make_admin_client()
        data = {
            "name": "Livraison express",
            "description": "24h",
            "amount": "5000.00",
            "currency": "XOF",
            "position": 0,
            "is_default": False,
            "is_active": True,
        }
        response = client.post(CREATE_URL, data=data, format="json")
        assert response.status_code == 201
        assert DeliveryOption.objects.filter(name="Livraison express").exists()

    def test_admin_can_update_delivery_option(self, db):
        client = _make_admin_client()
        opt = DeliveryOptionFactory()
        response = client.patch(update_url(opt.id), data={"name": "Modifié", "amount": "3000", "currency": "XOF", "position": 0, "is_default": False, "is_active": True, "description": ""}, format="json")
        assert response.status_code == 200
        opt.refresh_from_db()
        assert opt.name == "Modifié"

    def test_admin_can_delete_delivery_option(self, db):
        client = _make_admin_client()
        opt = DeliveryOptionFactory()
        response = client.delete(delete_url(opt.id))
        assert response.status_code == 204
        assert not DeliveryOption.objects.filter(id=opt.id).exists()

    def test_only_one_default_after_create(self, db):
        client = _make_admin_client()
        DeliveryOptionFactory(is_default=True)
        data = {
            "name": "Nouvelle option",
            "description": "",
            "amount": "1000.00",
            "currency": "XOF",
            "position": 1,
            "is_default": True,
            "is_active": True,
        }
        client.post(CREATE_URL, data=data, format="json")
        assert DeliveryOption.objects.filter(is_default=True).count() == 1


@pytest.mark.integration
@pytest.mark.django_db
class TestHealthEndpoint:

    def test_health_returns_200(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == 200

    def test_health_returns_ok(self, api_client):
        assert api_client.get("/health/").json() == {"status": "ok"}