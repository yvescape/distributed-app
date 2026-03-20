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
            "card_number",
            "masked_card_number",
            "expiration_date",
            "cvv",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "masked_card_number",
        ]

    def get_masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"