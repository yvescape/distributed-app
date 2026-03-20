from django.contrib.auth import get_user_model
from rest_framework import serializers
from .profile import ProfileSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_email_verified",
            "created_at",
            "profile",
        )

    def get_profile(self, obj):
        if hasattr(obj, "profile"):
            return ProfileSerializer(obj.profile).data
        return None