from django.db import models
from decimal import Decimal
from .order import Order
from .delivery_option import DeliveryOption


class OrderPricing(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="pricing"
    )

    delivery_option = models.ForeignKey(
        DeliveryOption,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_pricings"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    delivery_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(
        max_length=10,
        default="XOF"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):

        # récupération du sous total depuis les items de la commande
        subtotal = sum(
            item.price * item.quantity
            for item in self.order.items.all()
        )

        delivery_price = (
            self.delivery_option.amount
            if self.delivery_option
            else Decimal("0")
        )

        self.subtotal = subtotal
        self.delivery_price = delivery_price
        self.total = subtotal + delivery_price

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pricing for order {self.order.id}"