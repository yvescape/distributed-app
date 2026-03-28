# tests/integration/test_health.py
import pytest


@pytest.mark.integration
@pytest.mark.django_db
class TestHealthEndpoint:

    def test_health_returns_200(self, api_client):
        response = api_client.get("/health/")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, api_client):
        response = api_client.get("/health/")
        assert response.json() == {"status": "ok"}

    def test_health_accessible_without_auth(self, api_client):
        """Le health check ne doit pas exiger d'authentification."""
        response = api_client.get("/health/")
        assert response.status_code == 200