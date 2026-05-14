from django.db import models
import uuid


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID utilisateur provenant du auth-service",
    )

    session_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID session pour les utilisateurs non connectés",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        """Total des items sans la livraison."""
        return sum(item.total for item in self.items.all())

    def __str__(self):
        return f"Order {self.id}"