"""
Tests unitaires — Modèles (Comment, Like, Rating).
"""
import uuid

import pytest
from django.db import IntegrityError

from interation_app.models.comment import Comment
from interation_app.models.like import Like
from interation_app.models.rating import Rating
from interation_app.tests.conftest import PRODUCT_ID, USER_ID, USER_ID_2, USER_EMAIL


pytestmark = [pytest.mark.django_db, pytest.mark.unit]


# ═══════════════════════════════════════════════════════════════════════
#  Comment
# ═══════════════════════════════════════════════════════════════════════

class TestCommentModel:

    def test_create_comment(self):
        comment = Comment.objects.create(
            user_id=USER_ID,
            user_email=USER_EMAIL,
            product_id=PRODUCT_ID,
            content="Excellent produit !",
        )
        assert comment.pk is not None
        assert comment.content == "Excellent produit !"
        assert comment.user_email == USER_EMAIL

    def test_str_with_email(self):
        comment = Comment(user_id=USER_ID, user_email=USER_EMAIL, product_id=PRODUCT_ID, content="x")
        assert USER_EMAIL in str(comment)

    def test_str_without_email(self):
        comment = Comment(user_id=USER_ID, user_email="", product_id=PRODUCT_ID, content="x")
        assert str(USER_ID) in str(comment)

    def test_unique_together_user_product(self):
        Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="Premier")
        with pytest.raises(IntegrityError):
            Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="Doublon")

    def test_different_users_same_product(self):
        Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="User 1")
        Comment.objects.create(user_id=USER_ID_2, product_id=PRODUCT_ID, content="User 2")
        assert Comment.objects.filter(product_id=PRODUCT_ID).count() == 2

    def test_ordering_is_newest_first(self):
        c1 = Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="Premier")
        c2 = Comment.objects.create(user_id=USER_ID_2, product_id=PRODUCT_ID, content="Deuxième")
        comments = list(Comment.objects.filter(product_id=PRODUCT_ID))
        assert comments[0].pk == c2.pk  # le plus récent en premier

    def test_uuid_primary_key_auto_generated(self):
        comment = Comment.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, content="Test")
        assert isinstance(comment.id, uuid.UUID)


# ═══════════════════════════════════════════════════════════════════════
#  Like
# ═══════════════════════════════════════════════════════════════════════

class TestLikeModel:

    def test_create_like(self):
        like = Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        assert like.pk is not None
        assert like.created_at is not None

    def test_unique_together_user_product(self):
        Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        with pytest.raises(IntegrityError):
            Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)

    def test_different_users_can_like_same_product(self):
        Like.objects.create(user_id=USER_ID, product_id=PRODUCT_ID)
        Like.objects.create(user_id=USER_ID_2, product_id=PRODUCT_ID)
        assert Like.objects.filter(product_id=PRODUCT_ID).count() == 2


# ═══════════════════════════════════════════════════════════════════════
#  Rating
# ═══════════════════════════════════════════════════════════════════════

class TestRatingModel:

    def test_create_rating(self):
        rating = Rating.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, value=4)
        assert rating.value == 4
        assert isinstance(rating.id, uuid.UUID)

    def test_str(self):
        rating = Rating(user_id=USER_ID, product_id=PRODUCT_ID, value=5)
        assert "5" in str(rating)

    def test_unique_together_user_product(self):
        Rating.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, value=3)
        with pytest.raises(IntegrityError):
            Rating.objects.create(user_id=USER_ID, product_id=PRODUCT_ID, value=5)