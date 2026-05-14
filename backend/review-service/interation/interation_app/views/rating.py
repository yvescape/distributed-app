# views/rating.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from ..models.rating import Rating
from ..serializers.rating import RatingSerializer
from ..services.product_client import product_exists


class RatingCreateUpdateView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]  # depuis l'URL

        if not product_exists(product_id):
            raise ValidationError({"product_id": "Produit introuvable"})

        Rating.objects.update_or_create(
            user_id=self.request.user.id,
            product_id=product_id,
            defaults={"value": serializer.validated_data["value"]}
        )