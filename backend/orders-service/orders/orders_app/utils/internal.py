# orders/utils/internal.py
from django.conf import settings
from rest_framework.permissions import BasePermission


class InternalServicePermission(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get("X-Internal-Token")
        return token == settings.INTERNAL_SERVICE_TOKEN