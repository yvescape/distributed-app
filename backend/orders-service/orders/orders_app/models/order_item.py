from django.db import models
import uuid
from .order import Order

class OrderItem(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    # produit (snapshot)
    product_id = models.UUIDField()
    product_name = models.CharField(max_length=150)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(default=1)

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"