from rest_framework import generics
from ..models.product import Product
from ..serializers.product_card import ProductCardSerializer
from ..serializers.product_detail import ProductDetailSerializer
from rest_framework.permissions import AllowAny


# 🔹 Liste des produits (Cards)
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductCardSerializer
    permission_classes = [AllowAny]


# 🔹 Détail d’un produit
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = "id"
    permission_classes = [AllowAny]