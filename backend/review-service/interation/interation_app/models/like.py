import uuid
from django.db import models


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.UUIDField()  # venant du users-service
    product_id = models.UUIDField()  # venant du products-service

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_id", "product_id")

    def __str__(self):
        return f"{self.user_id} liked {self.product_id}"