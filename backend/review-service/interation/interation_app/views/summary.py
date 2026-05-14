from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Avg
from ..models.like import Like
from ..models.rating import Rating
from ..serializers.summary import ProductInteractionSummarySerializer
from django.db.models import Count, Avg, Exists, OuterRef, Q
from rest_framework.permissions import AllowAny


class ProductInteractionSummaryView(generics.GenericAPIView):
    serializer_class = ProductInteractionSummarySerializer
    permission_classes = [AllowAny]


    def get(self, request, product_id):
        # Une seule requête pour likes + user_liked
        like_data = Like.objects.filter(product_id=product_id).aggregate(
            total_likes=Count("id"),
        )

        rating_data = Rating.objects.filter(product_id=product_id).aggregate(
            average_rating=Avg("value"),
            total_ratings=Count("id"),
        )

        user_liked = False
        if request.user.is_authenticated:
            user_liked = Like.objects.filter(
                product_id=product_id,
                user_id=request.user.id
            ).exists()

        return Response({
            "total_likes": like_data["total_likes"],
            "average_rating": round(rating_data["average_rating"] or 0, 1),
            "total_ratings": rating_data["total_ratings"],
            "liked": user_liked,
        })