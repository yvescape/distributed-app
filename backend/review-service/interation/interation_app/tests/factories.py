"""
Factories factory-boy pour les tests du review-service.
Chaque factory génère des données aléatoires valides par défaut
et peut être surchargée par paramètres dans les tests.
"""
import uuid

import factory
from factory.django import DjangoModelFactory

from interation_app.models.comment import Comment
from interation_app.models.like import Like
from interation_app.models.rating import Rating


class CommentFactory(DjangoModelFactory):
    """Commentaire avec utilisateur et produit aléatoires."""

    class Meta:
        model = Comment

    user_id = factory.LazyFunction(uuid.uuid4)
    user_email = factory.Faker("email")
    product_id = factory.LazyFunction(uuid.uuid4)
    content = factory.Faker("paragraph", nb_sentences=2, locale="fr_FR")


class LikeFactory(DjangoModelFactory):
    """Like avec utilisateur et produit aléatoires."""

    class Meta:
        model = Like

    user_id = factory.LazyFunction(uuid.uuid4)
    product_id = factory.LazyFunction(uuid.uuid4)


class RatingFactory(DjangoModelFactory):
    """Note entre 1 et 5 avec utilisateur et produit aléatoires."""

    class Meta:
        model = Rating

    user_id = factory.LazyFunction(uuid.uuid4)
    product_id = factory.LazyFunction(uuid.uuid4)
    value = factory.Faker("random_int", min=1, max=5)
