from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..serializers.update_user import UpdateUserSerializer

    
class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user