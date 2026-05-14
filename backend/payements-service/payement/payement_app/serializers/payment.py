from rest_framework import serializers
from ..models.payment import Payment
import re


class PaymentSerializer(serializers.ModelSerializer):

    # champs de simulation de carte
    card_number = serializers.CharField(write_only=True)
    card_holder = serializers.CharField(write_only=True)
    expiration_date = serializers.CharField(write_only=True)
    cvv = serializers.CharField(write_only=True)

    # champs order_id
    order_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_pricing_id",
            "order_id",
            "amount",
            "currency",
            "status",
            "transaction_reference",
            "created_at",
            "card_number",
            "card_holder",
            "expiration_date",
            "cvv",
        ]

        read_only_fields = [
            "id",
            "status",
            "transaction_reference",
            "created_at",
        ]

    def create(self, validated_data):

        card_number = validated_data.pop("card_number")
        validated_data.pop("card_holder")
        validated_data.pop("expiration_date")
        validated_data.pop("cvv")
        order_id = validated_data.pop("order_id")

        # simulation : vérifier si la carte ressemble à une carte prépayée
        # règle simple : 16 chiffres
        if re.fullmatch(r"\d{16}", card_number):
            status = "success"
        else:
            status = "failed"

        payment = Payment.objects.create(
            status=status,
            **validated_data
        )

        payment._order_id = order_id

        return payment