from django.db import models
import uuid
from .order import Order


class OrderItem(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )

    product_id = models.UUIDField()

    # Snapshot produit figé à la commande
    product_name = models.CharField(max_length=150)
    product_image = models.URLField(blank=True)
    product_size = models.CharField(max_length=20, blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix unitaire figé au moment de la commande",
    )

    quantity = models.PositiveIntegerField(default=1)

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix total par produit commander",
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"