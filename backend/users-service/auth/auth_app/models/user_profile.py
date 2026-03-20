from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"