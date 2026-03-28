from rest_framework import serializers
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.order_address import OrderAddress


# -----------------------------
# Order Address
# -----------------------------
class OrderAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderAddress
        fields = [
            "id",
            "city",
            "address_line",
            "postal_code",
        ]
        read_only_fields = ["id"]