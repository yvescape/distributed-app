from rest_framework import serializers
from ..models.order_pricing import OrderPricing


class OrderPricingSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPricing
        fields = [
            "order",
            "delivery_option",
            "subtotal",
            "delivery_price",
            "total",
            "currency",
            "updated_at",
        ]
        read_only_fields = [
            "subtotal",
            "delivery_price",
            "total",
            "currency",
            "updated_at",
        ]