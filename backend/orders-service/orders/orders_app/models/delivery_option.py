from django.db import models
import uuid


class DeliveryOption(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        max_length=100,
        help_text="Nom du mode de livraison (ex: Livraison standard)"
    )

    description = models.CharField(
        max_length=100,
        blank=True,
        help_text="3–5 jours ouvrés"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Prix de la livraison"
    )

    currency = models.CharField(
        max_length=10,
        default="XOF"
    )

    position = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(
        default=True,
        help_text="Indique si cette option est disponible"
    )

    # option par défaut
    is_default = models.BooleanField(
        default=False,
        help_text="Définit cette option comme livraison par défaut"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # s'assurer qu'une seule option est par défaut
        if self.is_default:
            DeliveryOption.objects.filter(is_default=True).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.description}"