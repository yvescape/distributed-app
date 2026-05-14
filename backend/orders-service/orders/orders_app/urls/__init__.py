# urls/__init__.py
from django.urls import include, path

# Importer les patterns de chaque module
from .order import urlpatterns as order_patterns
from .order_item import urlpatterns as order_item_patterns
from .order_address import urlpatterns as order_address_patterns
from .delivery_option import urlpatterns as delivery_patterns
from .order_pricing import urlpatterns as order_pricing_patterns
from .order_internal import urlpatterns as order_internal_patterns

# Structure finale des URLs
urlpatterns = [
    # Routes pour les commandes
    path('', include(order_patterns)),
    
    # Routes pour les items commandes
    path('orders_item/', include(order_item_patterns)),

    # Routes pour address de la commande
    path('orders_address/', include(order_address_patterns)),
    
    # Routes pour les options de livraison
    path('delivery-options/', include(delivery_patterns)),

    # Routes pour les prix total de la commande
    path('<uuid:order_id>/pricing/', include(order_pricing_patterns)),

    # Routes pour confirmer la commande
    path('internal/', include(order_internal_patterns)),
]