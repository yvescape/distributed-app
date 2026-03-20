from django.db import models
import uuid


class Payment(models.Model):

    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # commande provenant du orders-service
    order_pricing_id = models.UUIDField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0
    )

    currency = models.CharField(
        max_length=10,
        default="XOF"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    transaction_reference = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.order_pricing_id} - {self.status}"