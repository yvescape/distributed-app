"""
Tests unitaires — Serializers.
"""
import uuid

import pytest

from interation_app.serializers.comment import CommentSerializer
from interation_app.serializers.like import LikeSerializer
from interation_app.serializers.rating import RatingSerializer
from interation_app.serializers.summary import ProductInteractionSummarySerializer
from interation_app.tests.conftest import PRODUCT_ID, USER_ID, USER_EMAIL


pytestmark = pytest.mark.unit


# ═══════════════════════════════════════════════════════════════════════
#  CommentSerializer
# ═══════════════════════════════════════════════════════════════════════

class TestCommentSerializer:

    def test_valid_data(self):
        data = {"content": "Super produit"}
        serializer = CommentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_content_is_invalid(self):
        serializer = CommentSerializer(data={"content": ""})
        assert not serializer.is_valid()
        assert "content" in serializer.errors

    def test_missing_content_is_invalid(self):
        serializer = CommentSerializer(data={})
        assert not serializer.is_valid()
        assert "content" in serializer.errors

    def test_read_only_fields_ignored_on_input(self):
        data = {
            "content": "Test",
            "user_id": str(USER_ID),
            "product_id": str(PRODUCT_ID),
            "user_email": USER_EMAIL,
        }
        serializer = CommentSerializer(data=data)
        assert serializer.is_valid()
        # Les champs read_only ne sont pas dans validated_data
        assert "user_id" not in serializer.validated_data
        assert "product_id" not in serializer.validated_data
        assert "user_email" not in serializer.validated_data


# ═══════════════════════════════════════════════════════════════════════
#  RatingSerializer
# ═══════════════════════════════════════════════════════════════════════

class TestRatingSerializer:

    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5])
    def test_valid_values(self, value):
        serializer = RatingSerializer(data={"value": value})
        assert serializer.is_valid(), serializer.errors

    @pytest.mark.parametrize("value", [0, -1, 6, 100])
    def test_invalid_values(self, value):
        serializer = RatingSerializer(data={"value": value})
        assert not serializer.is_valid()
        assert "value" in serializer.errors

    def test_missing_value(self):
        serializer = RatingSerializer(data={})
        assert not serializer.is_valid()
        assert "value" in serializer.errors

    def test_read_only_fields_ignored(self):
        data = {"value": 4, "user_id": str(USER_ID), "product_id": str(PRODUCT_ID)}
        serializer = RatingSerializer(data=data)
        assert serializer.is_valid()
        assert "user_id" not in serializer.validated_data


# ═══════════════════════════════════════════════════════════════════════
#  LikeSerializer
# ═══════════════════════════════════════════════════════════════════════

class TestLikeSerializer:

    def test_all_fields_read_only(self):
        """Le LikeSerializer n'a aucun champ writable — tout vient de la vue."""
        serializer = LikeSerializer(data={})
        assert serializer.is_valid()  # Pas de champ requis en écriture


# ═══════════════════════════════════════════════════════════════════════
#  ProductInteractionSummarySerializer
# ═══════════════════════════════════════════════════════════════════════

class TestSummarySerializer:

    def test_valid_data(self):
        data = {
            "product_id": str(PRODUCT_ID),
            "likes_count": 10,
            "average_rating": 4.2,
        }
        serializer = ProductInteractionSummarySerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_field(self):
        serializer = ProductInteractionSummarySerializer(data={"product_id": str(PRODUCT_ID)})
        assert not serializer.is_valid()