from rest_framework import generics
from ..models.rating import Rating
from ..serializers.rating import RatingSerializer
from rest_framework.permissions import IsAuthenticated


class RatingCreateUpdateView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_id = self.request.user.id
        product_id = serializer.validated_data["product_id"]

        rating, created = Rating.objects.update_or_create(
            user_id=user_id,
            product_id=product_id,
            defaults={"value": serializer.validated_data["value"]}
        )