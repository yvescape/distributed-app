from rest_framework import serializers
from ..models.user_audit_log import UserAuditLog
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Chercher l'utilisateur manuellement pour distinguer les cas
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Identifiants invalides.")

        if not user.check_password(data["password"]):
            raise serializers.ValidationError("Identifiants invalides.")

        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé.")

        refresh = RefreshToken.for_user(user)

        UserAuditLog.objects.create(user=user, action="LOGIN")

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }