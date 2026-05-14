# models/comment.py
import uuid
from django.db import models


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.UUIDField()
    user_email = models.CharField(max_length=150, blank=True, default="")
    product_id = models.UUIDField()

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user_id", "product_id")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user_email or self.user_id}"