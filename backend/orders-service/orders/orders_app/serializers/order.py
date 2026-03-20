from rest_framework import serializers
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.order_address import OrderAddress
from .order_item import OrderItemSerializer
from .order_address import OrderAddressSerializer


# -----------------------------
# Create Order
# -----------------------------
class OrderCreateSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)
    address = OrderAddressSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "user_id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "items",
            "address",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):

        items_data = validated_data.pop("items")
        address_data = validated_data.pop("address")

        order = Order.objects.create(**validated_data)

        total = 0

        for item in items_data:

            subtotal = item["price"] * item["quantity"]

            OrderItem.objects.create(
                order=order,
                subtotal=subtotal,
                **item
            )

            total += subtotal

        OrderAddress.objects.create(
            order=order,
            **address_data
        )

        order.total_amount = total
        order.save()

        return order


# -----------------------------
# Order Detail
# -----------------------------
class OrderDetailSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)
    address = OrderAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user_id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "status",
            "total_amount",
            "items",
            "address",
            "created_at",
        ]


# -----------------------------
# Order Post Payement
# -----------------------------
class OrderStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ["status"]