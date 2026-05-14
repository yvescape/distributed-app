# serializers/like.py
from rest_framework import serializers
from ..models.like import Like


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ["product_id", "user_id", "created_at"]
        read_only_fields = ["product_id", "user_id", "created_at"]