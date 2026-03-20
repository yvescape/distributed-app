from django.db import models
import uuid

class Product(models.Model):

    CATEGORY_CHOICES = [
        ("Eau de Parfum", "Eau de Parfum"),
        ("Eau de Toilette", "Eau de Toilette"),
        ("Extrait de Parfum", "Extrait de Parfum"),
    ]

    FAMILY_CHOICES = [
        ("Floral", "Floral"),
        ("Boisé", "Boisé"),
        ("Oriental", "Oriental"),
        ("Fruité", "Fruité"),
        ("Aromatique", "Aromatique"),
    ]

    GENDER_CHOICES = [
        ("Homme", "Homme"),
        ("Femme", "Femme"),
        ("Unisexe", "Unisexe"),
    ]

    # Informations principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=20)
    image = models.URLField()
    badge = models.CharField(max_length=50, blank=True, null=True)

    # Classification
    family = models.CharField(max_length=50, choices=FAMILY_CHOICES)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)

    # Notes olfactives (séparées proprement)
    notes_top = models.TextField(
        blank=True,
        help_text="Notes de tête (ex: Bergamote, Citron)"
    )
    notes_heart = models.TextField(
        blank=True,
        help_text="Notes de cœur (ex: Jasmin, Fleur d'oranger)"
    )
    notes_base = models.TextField(
        blank=True,
        help_text="Notes de fond (ex: Musc blanc, Santal)"
    )

    # Composition
    composition = models.TextField(
        blank=True,
        help_text="Liste des ingrédients"
    )

    # Conseils d'utilisation
    advice = models.TextField(
        blank=True,
        help_text="Conseils d'application et précautions"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name