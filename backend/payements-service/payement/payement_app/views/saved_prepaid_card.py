from rest_framework import generics, permissions
from ..models.prepay_cart import SavedPrepaidCard
from ..serializers.saved_prepaid_card import SavedPrepaidCardSerializer


class SavedPrepaidCardListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedPrepaidCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        return SavedPrepaidCard.objects.filter(
            user_id=user_id
        ).order_by("-created_at")


class SavedPrepaidCardDeleteView(generics.DestroyAPIView):

    queryset = SavedPrepaidCard.objects.all()
    serializer_class = SavedPrepaidCardSerializer
    permission_classes = [permissions.IsAuthenticated]