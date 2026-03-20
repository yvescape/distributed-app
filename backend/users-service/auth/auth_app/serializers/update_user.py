from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models.user_audit_log import UserAuditLog

User = get_user_model()


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        UserAuditLog.objects.create(
            user=instance,
            action="UPDATE",
        )

        return instance