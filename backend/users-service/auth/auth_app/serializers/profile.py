from rest_framework import serializers
from ..models.user_profile import UserProfile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "phone_number",
            "avatar",
            "bio",
            "country",
        )