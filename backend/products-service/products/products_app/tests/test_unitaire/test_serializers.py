# products_app/tests/tests_unitaire/test_serializers.py
import pytest
from decimal import Decimal
from products_app.serializers.product_card import ProductCardSerializer
from products_app.serializers.product_detail import ProductDetailSerializer
from ..factories import ProductFactory


@pytest.mark.unit
class TestProductCardSerializer:

    def test_expected_fields(self, db):
        product = ProductFactory()
        data = ProductCardSerializer(product).data
        expected = {"id", "name", "category", "price", "size", "image", "notes", "badge"}
        assert set(data.keys()) == expected

    def test_notes_combines_all_three(self, db):
        product = ProductFactory(
            notes_top="Bergamote",
            notes_heart="Jasmin",
            notes_base="Musc",
        )
        data = ProductCardSerializer(product).data
        assert data["notes"] == "Bergamote · Jasmin · Musc"

    def test_notes_skips_empty_parts(self, db):
        product = ProductFactory(notes_top="Citron", notes_heart="", notes_base="Santal")
        data = ProductCardSerializer(product).data
        assert data["notes"] == "Citron · Santal"

    def test_notes_empty_when_all_blank(self, db):
        product = ProductFactory(notes_top="", notes_heart="", notes_base="")
        data = ProductCardSerializer(product).data
        assert data["notes"] == ""

    def test_notes_only_top(self, db):
        product = ProductFactory(notes_top="Bergamote", notes_heart="", notes_base="")
        data = ProductCardSerializer(product).data
        assert data["notes"] == "Bergamote"

    def test_badge_can_be_null(self, db):
        product = ProductFactory(badge=None)
        data = ProductCardSerializer(product).data
        assert data["badge"] is None

    def test_badge_value_present(self, db):
        product = ProductFactory(badge="Nouveau")
        data = ProductCardSerializer(product).data
        assert data["badge"] == "Nouveau"

    def test_detail_fields_not_in_card(self, db):
        """Les champs détail ne doivent pas apparaître dans la card."""
        product = ProductFactory()
        data = ProductCardSerializer(product).data
        hidden = {"notes_top", "notes_heart", "notes_base", "composition", "advice",
                  "family", "gender", "created_at", "updated_at"}
        assert not hidden.intersection(set(data.keys()))

    def test_price_is_string_decimal(self, db):
        product = ProductFactory(price=Decimal("79.90"))
        data = ProductCardSerializer(product).data
        assert data["price"] == "79.90"


@pytest.mark.unit
class TestProductDetailSerializer:

    def test_contains_all_fields(self, db):
        product = ProductFactory()
        data = ProductDetailSerializer(product).data
        expected = {
            "id", "name", "category", "price", "size", "image", "badge",
            "family", "gender", "notes_top", "notes_heart", "notes_base",
            "composition", "advice", "created_at", "updated_at",
        }
        assert expected.issubset(set(data.keys()))

    def test_notes_fields_separate(self, db):
        product = ProductFactory(
            notes_top="Bergamote",
            notes_heart="Jasmin",
            notes_base="Musc",
        )
        data = ProductDetailSerializer(product).data
        assert data["notes_top"] == "Bergamote"
        assert data["notes_heart"] == "Jasmin"
        assert data["notes_base"] == "Musc"

    def test_composition_present(self, db):
        product = ProductFactory(composition="Alcohol, Aqua, Parfum")
        data = ProductDetailSerializer(product).data
        assert data["composition"] == "Alcohol, Aqua, Parfum"

    def test_advice_present(self, db):
        product = ProductFactory(advice="Vaporiser sur les poignets.")
        data = ProductDetailSerializer(product).data
        assert data["advice"] == "Vaporiser sur les poignets."

    def test_id_is_uuid_string(self, db):
        product = ProductFactory()
        data = ProductDetailSerializer(product).data
        import uuid
        uuid.UUID(data["id"])  # lève ValueError si invalide