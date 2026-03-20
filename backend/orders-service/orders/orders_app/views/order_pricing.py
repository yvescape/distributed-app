from rest_framework import generics
from ..models.order_pricing import OrderPricing
from ..serializers.order_pricing import OrderPricingSerializer

class OrderPricingDetailView(generics.RetrieveAPIView):
    queryset = OrderPricing.objects.all()
    serializer_class = OrderPricingSerializer
    lookup_field = "order_id"