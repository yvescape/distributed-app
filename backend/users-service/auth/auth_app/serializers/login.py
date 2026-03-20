from rest_framework import serializers
from ..models.user_audit_log import UserAuditLog
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data["email"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Identifiants invalides.")

        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé.")

        refresh = RefreshToken.for_user(user)

        # Log login
        UserAuditLog.objects.create(
            user=user,
            action="LOGIN",
        )

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }