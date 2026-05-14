"""
Tests unitaires — Services (order_client).
"""
import pytest
import requests

from payement_app.services.order_client import confirm_order, cancel_order

pytestmark = pytest.mark.unit


class TestConfirmOrder:

    def test_confirm_success(self, mocker):
        mock_patch = mocker.patch(
            "payement_app.services.order_client.requests.patch",
            return_value=mocker.Mock(status_code=200, json=lambda: {"status": "confirmed"}, raise_for_status=lambda: None),
        )
        result = confirm_order("some-order-id")
        assert result["status"] == "confirmed"
        mock_patch.assert_called_once()

    def test_confirm_failure_raises(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
        mocker.patch("payement_app.services.order_client.requests.patch", return_value=mock_resp)
        with pytest.raises(requests.HTTPError):
            confirm_order("some-order-id")


class TestCancelOrder:

    def test_cancel_success(self, mocker):
        mocker.patch(
            "payement_app.services.order_client.requests.patch",
            return_value=mocker.Mock(status_code=200, json=lambda: {"status": "cancelled"}, raise_for_status=lambda: None),
        )
        result = cancel_order("some-order-id")
        assert result["status"] == "cancelled"

    def test_cancel_failure_raises(self, mocker):
        mock_resp = mocker.Mock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
        mocker.patch("payement_app.services.order_client.requests.patch", return_value=mock_resp)
        with pytest.raises(requests.HTTPError):
            cancel_order("some-order-id")