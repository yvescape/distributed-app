# views/order_internal.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings
from ..models.order import Order
from ..models.order_pricing import OrderPricing
from ..serializers.order import OrderDetailSerializer
from rest_framework.permissions import BasePermission


class InternalServicePermission(BasePermission):
    """Vérifie le token des microservices internes."""

    def has_permission(self, request, view):
        token = request.headers.get("X-Internal-Token")
        return token == settings.INTERNAL_SERVICE_TOKEN


class InternalOrderConfirmView(APIView):
    """Confirmer une commande — appelé par payments-service."""

    permission_classes = [InternalServicePermission]

    def patch(self, request, pk):
        order = Order.objects.filter(pk=pk, status="pending").first()
        if not order:
            return Response({"error": "Commande non trouvée ou déjà traitée"}, status=404)

        if not order.items.exists():
            raise ValidationError("La commande doit contenir au moins un produit.")

        if not hasattr(order, "address"):
            raise ValidationError("L'adresse de livraison est requise.")

        order.status = "confirmed"
        order.save()

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


class InternalOrderCancelView(APIView):
    """Annuler une commande — appelé par payments-service."""

    permission_classes = [InternalServicePermission]

    def patch(self, request, pk):
        order = Order.objects.filter(
            pk=pk,
            status__in=["pending", "confirmed"],
        ).first()
        if not order:
            return Response({"error": "Commande non trouvée"}, status=404)

        order.status = "cancelled"
        order.save()

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)