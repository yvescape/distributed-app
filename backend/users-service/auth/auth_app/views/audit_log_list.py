from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from ..serializers.audit_log import AuditLogSerializer
from ..models.user_audit_log import UserAuditLog


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    queryset = UserAuditLog.objects.all().order_by("-timestamp")