from rest_framework import serializers
from ..models.product import Product


# 🔹 Serializer pour affichage en card
class ProductCardSerializer(serializers.ModelSerializer):
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "price",
            "size",
            "image",
            "notes",
            "badge",
        ]

    def get_notes(self, obj):
        parts = []
        if obj.notes_top:
            parts.append(obj.notes_top)
        if obj.notes_heart:
            parts.append(obj.notes_heart)
        if obj.notes_base:
            parts.append(obj.notes_base)
        return " · ".join(parts)