import requests
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from ..models.payment import Payment
from ..serializers.payment import PaymentSerializer
from django.conf import settings


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        payment = serializer.save()

        if payment.status != "success":
            return

        url = f"{settings.ORDERS_SERVICE_URL}/internal/{payment._order_id}/confirm/"
        headers = {
            "X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN,
        }

        response = requests.patch(url, headers=headers, timeout=5)

        if response.status_code != 200:
            payment.status = "failed"
            payment.save()
            raise Exception(f"Order confirmation failed: {response.text}")


class PaymentDetailView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = "transaction_reference"
    permission_classes = [permissions.IsAuthenticated]


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_pricing_id = self.request.query_params.get("order_pricing_id")
        qs = Payment.objects.all().order_by("-created_at")
        if order_pricing_id:
            return qs.filter(order_pricing_id=order_pricing_id)
        return qs