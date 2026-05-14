# payments-service/services/order_client.py
import requests
from django.conf import settings


ORDERS_SERVICE_URL = settings.ORDERS_SERVICE_URL
INTERNAL_API_KEY = settings.INTERNAL_API_KEY


def confirm_order(order_id):
    """Appelé après paiement réussi."""
    response = requests.patch(
        f"{ORDERS_SERVICE_URL}/internal/orders/{order_id}/confirm/",
        headers={
            "X-Internal-Api-Key": INTERNAL_API_KEY,
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    return response.json()


def cancel_order(order_id):
    """Appelé après échec de paiement."""
    response = requests.patch(
        f"{ORDERS_SERVICE_URL}/internal/orders/{order_id}/cancel/",
        headers={
            "X-Internal-Api-Key": INTERNAL_API_KEY,
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    return response.json()