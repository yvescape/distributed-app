from django.db import models
import uuid
from .order import Order


class OrderAddress(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.OneToOneField(
        Order,
        related_name="address",
        on_delete=models.CASCADE
    )
    
    city = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.city} - {self.address_line}"