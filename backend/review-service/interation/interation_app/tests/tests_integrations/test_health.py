"""
Tests d'intégration — Health check.
"""
import pytest
from django.test import Client


pytestmark = pytest.mark.integration


class TestHealthCheck:

    def test_health_returns_ok(self):
        client = Client()
        resp = client.get("/health/")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}