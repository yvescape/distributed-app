# views/order_item.py
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.order_pricing import OrderPricing
from ..serializers.order_item import OrderItemSerializer
from ..services.product_client import get_product_snapshot, product_exists


class OrderItemListCreateView(ListCreateAPIView):

    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny]

    def get_pending_order(self, create=False):
        request = self.request

        if request.user and request.user.is_authenticated:
            if create:
                order, _ = Order.objects.get_or_create(
                    user_id=request.user.id,
                    status="pending",
                )
                return order
            return Order.objects.filter(
                user_id=request.user.id,
                status="pending",
            ).first()

        session_id = (
            request.query_params.get("session_id")
            or request.data.get("session_id")
        )

        if session_id:
            if create:
                order, _ = Order.objects.get_or_create(
                    session_id=session_id,
                    status="pending",
                )
                return order
            return Order.objects.filter(
                session_id=session_id,
                status="pending",
            ).first()

        if create:
            raise ValidationError("Authentification ou session_id requis.")

        return None

    def get_queryset(self):
        order = self.get_pending_order(create=False)
        if order:
            return OrderItem.objects.filter(order=order)
        return OrderItem.objects.none()

    def _update_order_pricing(self, order):
        pricing, _ = OrderPricing.objects.get_or_create(order=order)
        pricing.calculate_and_save()

    def perform_create(self, serializer):
        product_id = serializer.validated_data["product_id"]

        # Vérifier que le produit existe avant toute création
        if not product_exists(product_id):
            raise ValidationError(
                {"product_id": f"Le produit '{product_id}' n'existe pas."}
            )

        order = self.get_pending_order(create=True)
        serializer.validated_data.pop("session_id", None)

        # Si le produit existe déjà, on incrémente de 1
        existing_item = OrderItem.objects.filter(
            order=order,
            product_id=product_id,
        ).first()

        if existing_item:
            existing_item.quantity += 1
            existing_item.total = existing_item.price * existing_item.quantity
            existing_item.save()
            serializer.instance = existing_item
        else:
            snapshot = get_product_snapshot(product_id)
            price = snapshot["price"]
            serializer.save(
                order=order,
                price=price,
                quantity=1,
                total=price,
                product_name=snapshot["name"],
                product_image=snapshot["image"],
                product_size=snapshot["size"],
            )

        self._update_order_pricing(order)


class OrderItemDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"

    def get_queryset(self):
        request = self.request

        if request.user and request.user.is_authenticated:
            return OrderItem.objects.filter(
                order__user_id=request.user.id,
                order__status="pending",
            )

        session_id = request.query_params.get("session_id")
        if session_id:
            return OrderItem.objects.filter(
                order__session_id=session_id,
                order__status="pending",
            )

        return OrderItem.objects.none()

    def _update_or_delete_order(self, order):
        if not order.items.exists():
            OrderPricing.objects.filter(order=order).delete()
            order.delete()
            return

        pricing, _ = OrderPricing.objects.get_or_create(order=order)
        pricing.calculate_and_save()

    def perform_update(self, serializer):
        quantity = serializer.validated_data.get("quantity")
        order = serializer.instance.order

        if quantity is not None and quantity <= 0:
            serializer.instance.delete()
            self._update_or_delete_order(order)
            return

        if quantity is not None:
            serializer.validated_data["total"] = serializer.instance.price * quantity

        serializer.save()
        self._update_or_delete_order(order)

    def perform_destroy(self, instance):
        order = instance.order
        instance.delete()
        self._update_or_delete_order(order)


class OrderItemQuantityView(APIView):
    """Endpoint léger pour les boutons +/- du frontend."""

    permission_classes = [AllowAny]

    def get_item(self, pk, request):
        if request.user and request.user.is_authenticated:
            return OrderItem.objects.filter(
                pk=pk,
                order__user_id=request.user.id,
                order__status="pending",
            ).first()

        session_id = request.query_params.get("session_id")
        if session_id:
            return OrderItem.objects.filter(
                pk=pk,
                order__session_id=session_id,
                order__status="pending",
            ).first()

        return None

    def patch(self, request, pk):
        item = self.get_item(pk, request)
        if not item:
            return Response({"error": "Item non trouvé"}, status=404)

        action = request.data.get("action")
        amount = int(request.data.get("amount", 1))

        if amount < 1:
            return Response({"error": "Amount doit être >= 1"}, status=400)

        if action == "increment":
            item.quantity += amount
            item.total = item.price * item.quantity
            item.save()

        elif action == "decrement":
            new_quantity = item.quantity - amount

            if new_quantity <= 0:
                order = item.order
                item.delete()

                if not order.items.exists():
                    OrderPricing.objects.filter(order=order).delete()
                    order.delete()
                    return Response({"message": "Item et commande supprimés"})

                pricing, _ = OrderPricing.objects.get_or_create(order=order)
                pricing.calculate_and_save()
                return Response({"message": "Item supprimé"})

            item.quantity = new_quantity
            item.total = item.price * item.quantity
            item.save()

        else:
            return Response(
                {"error": "Action invalide. Utilisez 'increment' ou 'decrement'"},
                status=400,
            )

        pricing, _ = OrderPricing.objects.get_or_create(order=item.order)
        pricing.calculate_and_save()

        serializer = OrderItemSerializer(item)
        return Response(serializer.data)


class ProductInCartView(APIView):
    """Vérifie si un produit existe dans le panier (order pending) d'un utilisateur ou d'une session."""

    permission_classes = [AllowAny]

    def get(self, request, product_id):
        # Résoudre la commande pending via user ou session_id
        if request.user and request.user.is_authenticated:
            order = Order.objects.filter(
                user_id=request.user.id,
                status="pending",
            ).first()
        else:
            session_id = request.query_params.get("session_id")
            if not session_id:
                return Response(
                    {"error": "Authentification ou session_id requis."},
                    status=400,
                )
            order = Order.objects.filter(
                session_id=session_id,
                status="pending",
            ).first()

        if not order:
            return Response({
                "in_cart": False,
                "product_id": product_id,
                "quantity": 0,
            })

        item = OrderItem.objects.filter(
            order=order,
            product_id=product_id,
        ).first()

        if item:
            return Response({
                "in_cart": True,
                "product_id": product_id,
                "quantity": item.quantity,
                "item_id": item.id,
                "price": str(item.price),
                "total": str(item.total),
            })

        return Response({
            "in_cart": False,
            "product_id": product_id,
            "quantity": 0,
        })