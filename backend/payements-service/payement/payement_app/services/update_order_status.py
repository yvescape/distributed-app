import requests


def update_order_status(order_id, status):

    url = f"http://orders-service:8000/orders/{order_id}/status/"

    data = {
        "status": status
    }

    requests.patch(url, json=data)