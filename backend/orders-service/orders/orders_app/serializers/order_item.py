# serializers/order_item.py
from rest_framework import serializers
from ..models.order_item import OrderItem


class OrderItemSerializer(serializers.ModelSerializer):

    session_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "product_image",
            "product_size",
            "price",
            "quantity",
            "total",
            "session_id",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "product_image",
            "product_size",
            "price",
            "total",
        ]