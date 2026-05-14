"""
Tests unitaires — Service product_client.
"""
import pytest
import requests
from decimal import Decimal
from orders_app.services.product_client import product_exists, get_product_snapshot, get_product

pytestmark = pytest.mark.unit

PRODUCT_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"


class TestProductExists:

    def test_returns_true_on_200(self, mocker):
        mocker.patch("orders_app.services.product_client.requests.get", return_value=mocker.Mock(status_code=200))
        assert product_exists(PRODUCT_ID) is True

    def test_returns_false_on_404(self, mocker):
        mocker.patch("orders_app.services.product_client.requests.get", return_value=mocker.Mock(status_code=404))
        assert product_exists(PRODUCT_ID) is False

    def test_returns_false_on_timeout(self, mocker):
        mocker.patch("orders_app.services.product_client.requests.get", side_effect=requests.Timeout)
        assert product_exists(PRODUCT_ID) is False

    def test_returns_false_on_connection_error(self, mocker):
        mocker.patch("orders_app.services.product_client.requests.get", side_effect=requests.ConnectionError)
        assert product_exists(PRODUCT_ID) is False


class TestGetProductSnapshot:

    def test_returns_snapshot(self, mocker):
        mocker.patch(
            "orders_app.services.product_client.requests.get",
            return_value=mocker.Mock(
                status_code=200,
                json=lambda: {"price": "75.00", "name": "Parfum X", "image": "https://img.jpg", "size": "50ml"},
                raise_for_status=lambda: None,
            ),
        )
        snapshot = get_product_snapshot(PRODUCT_ID)
        assert snapshot["price"] == Decimal("75.00")
        assert snapshot["name"] == "Parfum X"
        assert snapshot["size"] == "50ml"