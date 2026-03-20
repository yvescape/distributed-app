from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models.like import Like

class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        user_id = request.user.id

        like = Like.objects.filter(
            user_id=user_id,
            product_id=product_id
        ).first()

        if like:
            like.delete()
            return Response({"message": "Like removed"})
        else:
            Like.objects.create(
                user_id=user_id,
                product_id=product_id
            )
            return Response({"message": "Product liked"})