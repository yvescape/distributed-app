from rest_framework import generics, permissions
from ..models.order import Order
from ..serializers.order import OrderCreateSerializer, OrderDetailSerializer, OrderStatusUpdateSerializer



class OrderCreateView(generics.CreateAPIView):

    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserOrderListView(generics.ListAPIView):

    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        user_id = self.request.user.id

        return Order.objects.filter(
            user_id=user_id
        ).order_by("-created_at")
    

class OrderDetailView(generics.RetrieveAPIView):

    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.AllowAny]


class OrderStatusUpdateView(generics.UpdateAPIView):

    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAdminUser]