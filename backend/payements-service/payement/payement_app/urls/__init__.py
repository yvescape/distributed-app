from django.urls import path, include

# Importer les deux ensembles d'URLs
from .payment import urlpatterns as payment_patterns
from .saved_prepaid_card import urlpatterns as saved_card_patterns

# URLs avec préfixes pour une meilleure organisation
urlpatterns = [
    path('payments/', include(payment_patterns)),
    path('saved-cards/', include(saved_card_patterns)),
]