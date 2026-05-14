# serializers/order_address.py
from rest_framework import serializers
from ..models.order_address import OrderAddress


class OrderAddressSerializer(serializers.ModelSerializer):

    session_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = OrderAddress
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "city",
            "address_line",
            "session_id",
        ]
        read_only_fields = ["id"]