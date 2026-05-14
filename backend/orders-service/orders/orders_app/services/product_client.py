import requests
from decimal import Decimal
from django.conf import settings


PRODUCTS_SERVICE_URL = "http://products:8000"


def get_product(product_id):
    """Récupère les infos complètes du produit depuis le products-service."""
    response = requests.get(
        f"{PRODUCTS_SERVICE_URL}/{product_id}/"
    )
    response.raise_for_status()
    return response.json()


def get_product_price(product_id):
    """Récupère uniquement le prix."""
    product = get_product(product_id)
    return Decimal(str(product["price"]))


def get_product_snapshot(product_id):
    """Récupère un snapshot des infos utiles pour la commande."""
    product = get_product(product_id)
    return {
        "price": Decimal(str(product["price"])),
        "name": product["name"],
        "image": product["image"],
        "size": product["size"],
    }

def product_exists(product_id: str) -> bool:
    try:
        resp = requests.get(
            f"{PRODUCTS_SERVICE_URL}/{product_id}/",
            timeout=3
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False