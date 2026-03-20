from rest_framework import generics, permissions
from ..models.delivery_option import DeliveryOption
from ..serializers.delivery_option import DeliveryOptionSerializer


class DeliveryOptionListView(generics.ListAPIView):

    queryset = DeliveryOption.objects.filter(is_active=True).order_by("position")
    serializer_class = DeliveryOptionSerializer
    permission_classes = [permissions.AllowAny]

class DeliveryOptionDetailView(generics.RetrieveAPIView):

    queryset = DeliveryOption.objects.filter(is_active=True)
    serializer_class = DeliveryOptionSerializer
    permission_classes = [permissions.AllowAny]

class DeliveryOptionCreateView(generics.CreateAPIView):

    queryset = DeliveryOption.objects.all()
    serializer_class = DeliveryOptionSerializer
    permission_classes = [permissions.IsAdminUser]

class DeliveryOptionUpdateView(generics.UpdateAPIView):

    queryset = DeliveryOption.objects.all()
    serializer_class = DeliveryOptionSerializer
    permission_classes = [permissions.IsAdminUser]

class DeliveryOptionDeleteView(generics.DestroyAPIView):

    queryset = DeliveryOption.objects.all()
    serializer_class = DeliveryOptionSerializer
    permission_classes = [permissions.IsAdminUser]