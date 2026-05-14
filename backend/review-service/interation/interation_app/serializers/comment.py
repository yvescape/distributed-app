# serializers/comment.py
from rest_framework import serializers
from ..models.comment import Comment


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "id",
            "product_id",
            "user_id",
            "user_email",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product_id", "user_id", "user_email", "created_at", "updated_at"]