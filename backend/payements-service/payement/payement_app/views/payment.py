from rest_framework import generics, permissions
from ..models.payment import Payment
from ..serializers.payment import PaymentSerializer


class PaymentCreateView(generics.CreateAPIView):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]


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
        qs = Payment.objects.all().order_by("-created_at")  # ← ajouter order_by
        if order_pricing_id:
            return qs.filter(order_pricing_id=order_pricing_id)
        return qs