# urls/__init__.py
from django.urls import include, path

# Importer les patterns de chaque module
from .order import urlpatterns as order_patterns
from .delivery_option import urlpatterns as delivery_patterns
from .order_pricing import urlpatterns as order_pricing_patterns

# Structure finale des URLs
urlpatterns = [
    # Routes pour les commandes
    path('orders/', include(order_patterns)),
    
    # Routes pour les options de livraison
    path('delivery/', include(delivery_patterns)),

    # Routes pour les prix total de la commande
    path('order-pricing/', include(order_pricing_patterns)),
]