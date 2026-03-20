from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models.user_profile import UserProfile
from ..models.user_audit_log import UserAuditLog

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        )
        read_only_fields = ("id",)

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        # Créer profil automatiquement
        UserProfile.objects.create(user=user)

        # Log audit
        UserAuditLog.objects.create(
            user=user,
            action="CREATE",
        )

        return user