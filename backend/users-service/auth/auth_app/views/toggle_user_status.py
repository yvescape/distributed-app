from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from ..models.user_audit_log import UserAuditLog

User = get_user_model()



class ToggleUserStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.is_active = not user.is_active
        user.save()

        UserAuditLog.objects.create(
            user=user,
            action="UPDATE",
        )

        return Response(
            {"detail": "Statut modifié.", "is_active": user.is_active},
            status=status.HTTP_200_OK,
        )