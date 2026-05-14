# views/delivery_option.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from ..models.delivery_option import DeliveryOption
from ..serializers.delivery_option import DeliveryOptionSerializer


class DeliveryOptionListView(ListAPIView):
    """Liste des options de livraison actives."""

    serializer_class = DeliveryOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return DeliveryOption.objects.filter(
            is_active=True
        ).order_by("position")


class DeliveryOptionDetailView(RetrieveAPIView):
    """Détail d'une option de livraison."""

    serializer_class = DeliveryOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return DeliveryOption.objects.filter(is_active=True)