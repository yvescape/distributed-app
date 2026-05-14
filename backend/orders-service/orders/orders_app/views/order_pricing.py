# views/order_pricing.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from ..models.order import Order
from ..models.order_pricing import OrderPricing
from ..models.delivery_option import DeliveryOption
from ..serializers.order_pricing import OrderPricingSerializer


class OrderPricingListView(ListAPIView):
    """Liste des pricings des commandes de l'utilisateur ou session."""

    serializer_class = OrderPricingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        request = self.request

        if request.user and request.user.is_authenticated:
            return OrderPricing.objects.filter(
                order__user_id=request.user.id,
            ).order_by("-updated_at")

        session_id = request.query_params.get("session_id")
        if session_id:
            return OrderPricing.objects.filter(
                order__session_id=session_id,
            ).order_by("-updated_at")

        return OrderPricing.objects.none()


class OrderPricingDetailView(RetrieveAPIView):
    """Détail du pricing d'une commande précise."""

    serializer_class = OrderPricingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        request = self.request

        if request.user and request.user.is_authenticated:
            return OrderPricing.objects.filter(
                order__user_id=request.user.id,
            )

        session_id = request.query_params.get("session_id")
        if session_id:
            return OrderPricing.objects.filter(
                order__session_id=session_id,
            )

        return OrderPricing.objects.none()


class UpdateDeliveryOptionView(APIView):
    """Modifier l'option de livraison d'une commande pending."""

    permission_classes = [AllowAny]

    def get_order(self, order_id, request):
        """Récupère la commande pending par user ou session."""
        if request.user and request.user.is_authenticated:
            return Order.objects.filter(
                id=order_id,
                user_id=request.user.id,
                status="pending",
            ).first()

        session_id = request.query_params.get("session_id")
        if session_id:
            return Order.objects.filter(
                id=order_id,
                session_id=session_id,
                status="pending",
            ).first()

        return None

    def patch(self, request, order_id):
        order = self.get_order(order_id, request)
        if not order:
            return Response(
                {"detail": "Commande introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        delivery_option_id = request.data.get("delivery_option_id")
        if not delivery_option_id:
            return Response(
                {"detail": "delivery_option_id est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            delivery_option = DeliveryOption.objects.get(
                id=delivery_option_id,
                is_active=True,
            )
        except DeliveryOption.DoesNotExist:
            return Response(
                {"detail": "Option de livraison invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pricing, _ = OrderPricing.objects.get_or_create(order=order)
        pricing.delivery_option = delivery_option
        pricing.delivery_price = delivery_option.amount
        pricing.total = pricing.subtotal + pricing.delivery_price
        pricing.save()

        serializer = OrderPricingSerializer(pricing)
        return Response(serializer.data)