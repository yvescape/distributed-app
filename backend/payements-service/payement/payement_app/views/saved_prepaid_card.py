from rest_framework import generics
from ..models.prepay_cart import SavedPrepaidCard
from ..serializers.saved_prepaid_card import SavedPrepaidCardSerializer


class SavedPrepaidCardListCreateView(generics.ListCreateAPIView):

    serializer_class = SavedPrepaidCardSerializer

    def get_queryset(self):

        user_id = self.request.query_params.get("user_id")

        return SavedPrepaidCard.objects.filter(user_id=user_id)

    def perform_create(self, serializer):

        user_id = self.request.data.get("user_id")

        serializer.save(user_id=user_id)


class SavedPrepaidCardDeleteView(generics.DestroyAPIView):

    queryset = SavedPrepaidCard.objects.all()
    serializer_class = SavedPrepaidCardSerializer