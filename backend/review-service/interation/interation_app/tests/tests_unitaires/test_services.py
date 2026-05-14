"""
Tests unitaires — Service product_client (appel HTTP mocké).
"""
import pytest
import requests

from interation_app.services.product_client import product_exists
from interation_app.tests.conftest import PRODUCT_ID


pytestmark = pytest.mark.unit


class TestProductExists:

    def test_returns_true_on_200(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.status_code = 200
        mocker.patch("interation_app.services.product_client.requests.get", return_value=mock_resp)

        assert product_exists(PRODUCT_ID) is True

    def test_returns_false_on_404(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.status_code = 404
        mocker.patch("interation_app.services.product_client.requests.get", return_value=mock_resp)

        assert product_exists(PRODUCT_ID) is False

    def test_returns_false_on_500(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.status_code = 500
        mocker.patch("interation_app.services.product_client.requests.get", return_value=mock_resp)

        assert product_exists(PRODUCT_ID) is False

    def test_returns_false_on_timeout(self, mocker):
        mocker.patch(
            "interation_app.services.product_client.requests.get",
            side_effect=requests.Timeout("timeout"),
        )
        assert product_exists(PRODUCT_ID) is False

    def test_returns_false_on_connection_error(self, mocker):
        mocker.patch(
            "interation_app.services.product_client.requests.get",
            side_effect=requests.ConnectionError("connection refused"),
        )
        assert product_exists(PRODUCT_ID) is False

    def test_calls_correct_url(self, mocker):
        mock_get = mocker.patch(
            "interation_app.services.product_client.requests.get",
            return_value=mocker.Mock(status_code=200),
        )
        product_exists(PRODUCT_ID)
        mock_get.assert_called_once_with(
            f"http://products:8000/{PRODUCT_ID}/",
            timeout=3,
        )