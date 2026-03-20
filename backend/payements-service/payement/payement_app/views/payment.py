from rest_framework import generics
from ..models.payment import Payment
from ..serializers.payment import PaymentSerializer


class PaymentCreateView(generics.CreateAPIView):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentDetailView(generics.RetrieveAPIView):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = "transaction_reference"


class PaymentListView(generics.ListAPIView):

    serializer_class = PaymentSerializer

    def get_queryset(self):

        order_pricing_id = self.request.query_params.get("order_pricing_id")

        if order_pricing_id:
            return Payment.objects.filter(order_pricing_id=order_pricing_id)

        return Payment.objects.all()