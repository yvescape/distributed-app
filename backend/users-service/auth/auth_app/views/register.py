from rest_framework import generics
from ..serializers.register import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]