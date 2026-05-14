# serializers/order_pricing.py
from rest_framework import serializers
from ..models.order_pricing import OrderPricing
from .delivery_option import DeliveryOptionSerializer


class OrderPricingSerializer(serializers.ModelSerializer):

    delivery_option = DeliveryOptionSerializer(read_only=True)

    class Meta:
        model = OrderPricing
        fields = [
            "id",
            "delivery_option",
            "subtotal",
            "delivery_price",
            "total",
            "currency",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "subtotal",
            "delivery_price",
            "total",
            "updated_at",
        ]