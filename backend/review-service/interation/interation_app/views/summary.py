from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Avg
from ..models.like import Like
from ..models.rating import Rating
from ..serializers.summary import ProductInteractionSummarySerializer


class ProductInteractionSummaryView(generics.GenericAPIView):
    serializer_class = ProductInteractionSummarySerializer

    def get(self, request, product_id):
        likes_count = Like.objects.filter(product_id=product_id).count()
        average_rating = Rating.objects.filter(product_id=product_id).aggregate(
            avg=Avg("value")
        )["avg"] or 0

        data = {
            "product_id": product_id,
            "likes_count": likes_count,
            "average_rating": round(average_rating, 2),
        }

        return Response(data)