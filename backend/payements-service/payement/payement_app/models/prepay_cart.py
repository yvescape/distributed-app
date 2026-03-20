from django.db import models
import uuid


class SavedPrepaidCard(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # utilisateur venant du users-service
    user_id = models.UUIDField()

    # informations carte (simulation)
    card_number = models.CharField(max_length=20)
    card_holder = models.CharField(max_length=150)
    expiration_date = models.CharField(max_length=5)
    cvv = models.CharField(max_length=4)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_holder} - {self.card_number[-4:]}"