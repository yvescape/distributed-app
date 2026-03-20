from rest_framework import serializers
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.order_address import OrderAddress


# -----------------------------
# Order Item
# -----------------------------
class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "price",
            "quantity",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal"]