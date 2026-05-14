# views/comment.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from ..models.comment import Comment
from ..serializers.comment import CommentSerializer
from ..services.product_client import product_exists


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        return Comment.objects.filter(product_id=product_id).order_by("-created_at")


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]
        user_id = self.request.user.id

        if not product_exists(product_id):
            raise ValidationError({"product_id": "Produit introuvable"})

        if Comment.objects.filter(user_id=user_id, product_id=product_id).exists():
            raise ValidationError({"detail": "Vous avez déjà commenté ce produit."})

        serializer.save(
            user_id=user_id,
            user_email=self.request.user.email,  # directement depuis le JWT
            product_id=product_id
        )


class CommentUpdateView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        product_id = self.kwargs["product_id"]
        user_id = self.request.user.id

        try:
            return Comment.objects.get(user_id=user_id, product_id=product_id)
        except Comment.DoesNotExist:
            raise ValidationError({"detail": "Aucun commentaire à modifier"})