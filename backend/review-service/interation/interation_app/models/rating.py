import uuid
from django.db import models


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.UUIDField()
    product_id = models.UUIDField()

    value = models.IntegerField()  # 1 à 5

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_id", "product_id")

    def __str__(self):
        return f"{self.value} stars"