from django.db import models
from decimal import Decimal
import uuid
from .order import Order
from .delivery_option import DeliveryOption


class OrderPricing(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="pricing",
    )

    delivery_option = models.ForeignKey(
        DeliveryOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_pricings",
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Somme des items, recalculée à chaque modification",
    )

    delivery_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Frais de livraison",
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    currency = models.CharField(max_length=10, default="FCFA")
    updated_at = models.DateTimeField(auto_now=True)

    def assign_default_delivery(self):
        """Assigne une option de livraison par défaut si aucune n'est définie."""
        if not self.delivery_option:
            default_option = DeliveryOption.objects.filter(
                is_default=True, is_active=True
            ).first()

            if not default_option:
                default_option = DeliveryOption.objects.filter(
                    is_active=True
                ).order_by("position").first()

            self.delivery_option = default_option

        self.delivery_price = (
            self.delivery_option.amount
            if self.delivery_option
            else Decimal("0")
        )

    def calculate_and_save(self):
        self.assign_default_delivery()

        self.subtotal = self.order.subtotal

        self.total = self.subtotal + self.delivery_price

        self.save()

    def __str__(self):
        return f"Pricing for order {self.order.id}"