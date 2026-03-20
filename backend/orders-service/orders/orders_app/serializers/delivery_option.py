from rest_framework import serializers
from ..models.delivery_option import DeliveryOption


class DeliveryOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryOption
        fields = [
            "id",
            "name",
            "description",
            "amount",
            "currency",
            "position",
            "is_default",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]