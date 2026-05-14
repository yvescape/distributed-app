import uuid
from django.db import models


class Like(models.Model):
    product_id = models.UUIDField()
    user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["product_id", "user_id"]),
        ]
        unique_together = ("product_id", "user_id")