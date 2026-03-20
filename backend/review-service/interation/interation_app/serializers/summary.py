from rest_framework import serializers


class ProductInteractionSummarySerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    likes_count = serializers.IntegerField()
    average_rating = serializers.FloatField()