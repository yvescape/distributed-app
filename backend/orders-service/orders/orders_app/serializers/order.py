# serializers/order.py
from rest_framework import serializers
from ..models.order import Order
from .order_item import OrderItemSerializer
from .order_address import OrderAddressSerializer
from .order_pricing import OrderPricingSerializer


class OrderDetailSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)
    address = OrderAddressSerializer(read_only=True)
    pricing = OrderPricingSerializer(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user_id",
            "session_id",
            "status",
            "subtotal",
            "items",
            "address",
            "pricing",
            "created_at",
            "updated_at",
        ]