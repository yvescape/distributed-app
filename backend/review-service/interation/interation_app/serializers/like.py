from rest_framework import serializers
from ..models.like import Like


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ["id", "product_id", "created_at"]
        read_only_fields = ["id", "created_at"]