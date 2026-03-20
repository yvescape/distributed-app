from rest_framework import generics
from ..models.comment import Comment
from ..serializers.comment import CommentSerializer
from rest_framework.permissions import IsAuthenticated


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return Comment.objects.filter(product_id=product_id).order_by("-created_at")


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)