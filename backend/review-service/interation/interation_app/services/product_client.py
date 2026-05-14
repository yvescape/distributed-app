# interation_app/services/services.py
import requests

PRODUCT_SERVICE_URL = "http://products:8000"

def product_exists(product_id: str) -> bool:
    try:
        resp = requests.get(
            f"{PRODUCT_SERVICE_URL}/{product_id}/",
            timeout=3
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False