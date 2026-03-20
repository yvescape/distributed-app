from rest_framework import serializers
from ..models.rating import Rating


class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = [
            "id",
            "product_id",
            "value",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_value(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value