# views/order_address.py
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from ..models.order import Order
from ..models.order_address import OrderAddress
from ..models.order_pricing import OrderPricing
from ..serializers.order_address import OrderAddressSerializer


class OrderAddressCreateUpdateView(CreateAPIView):
    """Ajouter ou modifier l'adresse d'une commande pending."""

    serializer_class = OrderAddressSerializer
    permission_classes = [AllowAny]

    def get_pending_order(self):
        request = self.request

        if request.user and request.user.is_authenticated:
            order = Order.objects.filter(
                user_id=request.user.id,
                status="pending",
            ).first()
        else:
            session_id = request.data.get("session_id")
            if not session_id:
                raise ValidationError("Authentification ou session_id requis.")
            order = Order.objects.filter(
                session_id=session_id,
                status="pending",
            ).first()

        if not order:
            raise ValidationError("Aucune commande en cours. Ajoutez d'abord un produit.")

        return order

    def perform_create(self, serializer):
        order = self.get_pending_order()
        serializer.validated_data.pop("session_id", None)

        existing_address = OrderAddress.objects.filter(order=order).first()

        if existing_address:
            for attr, value in serializer.validated_data.items():
                setattr(existing_address, attr, value)
            existing_address.save()
            serializer.instance = existing_address
        else:
            serializer.save(order=order)

class OrderAddressDetailView(RetrieveUpdateDestroyAPIView):
    """Consulter, modifier ou supprimer l'adresse."""

    serializer_class = OrderAddressSerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"

    def get_queryset(self):
        request = self.request

        if request.user and request.user.is_authenticated:
            return OrderAddress.objects.filter(
                order__user_id=request.user.id,
                order__status="pending",
            )

        session_id = request.query_params.get("session_id")
        if session_id:
            return OrderAddress.objects.filter(
                order__session_id=session_id,
                order__status="pending",
            )

        return OrderAddress.objects.none()