from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models.user_audit_log import UserAuditLog

User = get_user_model()


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserAuditLog
        fields = (
            "id",
            "user_email",
            "action",
            "ip_address",
            "timestamp",
        )