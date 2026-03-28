# serializers/saved_prepaid_card.py
from rest_framework import serializers
from ..models.prepay_cart import SavedPrepaidCard


class SavedPrepaidCardSerializer(serializers.ModelSerializer):

    masked_card_number = serializers.SerializerMethodField()

    class Meta:
        model = SavedPrepaidCard
        fields = [
            "id",
            "user_id",
            "card_holder",
            "card_number",       # ← ajouter
            "cvv",               # ← ajouter
            "masked_card_number",
            "expiration_date",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "masked_card_number",
        ]

        extra_kwargs = {
            "card_number": {"write_only": True},  # présent dans fields → write_only fonctionne
            "cvv": {"write_only": True},
        }

    def get_masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"