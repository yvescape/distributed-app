from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..serializers.profile import ProfileSerializer


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = self.request.user.profile.__class__.objects.get_or_create(
            user=self.request.user
        )
        return profile