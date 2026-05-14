# views/order.py
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models.order import Order
from ..serializers.order import OrderDetailSerializer


class UserOrderListView(ListAPIView):
    """Liste des commandes par user ou session."""

    serializer_class = OrderDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        request = self.request

        if request.user and request.user.is_authenticated:
            return Order.objects.filter(
                user_id=request.user.id,
            ).order_by("-created_at")

        session_id = request.query_params.get("session_id")
        if session_id:
            return Order.objects.filter(
                session_id=session_id,
            ).order_by("-created_at")

        return Order.objects.none()


class OrderDetailView(RetrieveAPIView):
    """Détail d'une commande."""

    serializer_class = OrderDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        request = self.request

        if request.user and request.user.is_authenticated:
            return Order.objects.filter(user_id=request.user.id)

        session_id = request.query_params.get("session_id")
        if session_id:
            return Order.objects.filter(session_id=session_id)

        return Order.objects.none()


class OrderConfirmView(UpdateAPIView):
    """Confirmer une commande — utilisateur connecté uniquement."""

    serializer_class = OrderDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Order.objects.filter(
            user_id=self.request.user.id,
            status="pending",
        )

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Vérifier que la commande a des items
        if not order.items.exists():
            raise ValidationError("La commande doit contenir au moins un produit.")

        # Vérifier que l'adresse existe
        if not hasattr(order, "address"):
            raise ValidationError("L'adresse de livraison est requise.")

        # Vérifier que l'adresse est complète
        address = order.address
        missing = []
        if not address.first_name:
            missing.append("first_name")
        if not address.last_name:
            missing.append("last_name")
        if not address.mobile:
            missing.append("mobile")

        if missing:
            raise ValidationError(
                f"Champs requis pour confirmer : {', '.join(missing)}"
            )

        # Confirmer
        order.status = "confirmed"
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

class OrderCancelView(UpdateAPIView):
    """Annuler une commande pending ou confirmed."""

    serializer_class = OrderDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Order.objects.filter(
            user_id=self.request.user.id,
            status__in=["pending", "confirmed"],
        )

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = "cancelled"
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
class ClaimGuestOrdersView(APIView):
    """Rattacher les commandes guest à l'utilisateur connecté."""

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        session_id = request.data.get("session_id")
        if not session_id:
            return Response({"error": "session_id requis"}, status=400)

        updated = Order.objects.filter(
            session_id=session_id,
            user_id__isnull=True,
        ).update(
            user_id=request.user.id,
            session_id=None,
        )

        return Response({"orders_claimed": updated})

class CartCountView(APIView):
    """Nombre d'items dans le panier pour le badge."""

    permission_classes = [AllowAny]

    def get(self, request):
        if request.user and request.user.is_authenticated:
            order = Order.objects.filter(
                user_id=request.user.id,
                status="pending",
            ).first()
        else:
            session_id = request.query_params.get("session_id")
            if session_id:
                order = Order.objects.filter(
                    session_id=session_id,
                    status="pending",
                ).first()
            else:
                return Response({"count": 0})

        if not order:
            return Response({"count": 0})

        count = sum(item.quantity for item in order.items.all())
        return Response({"count": count})