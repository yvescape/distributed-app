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

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)

    mobile = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}"