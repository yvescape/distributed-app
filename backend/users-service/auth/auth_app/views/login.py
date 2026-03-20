from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers.login import LoginSerializer


class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)