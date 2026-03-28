# products_app/tests/tests_unitaire/test_models.py
import uuid
import pytest
from decimal import Decimal
from django.utils import timezone
from products_app.models.product import Product
from ..factories import ProductFactory


@pytest.mark.unit
class TestProductModel:

    def test_product_creation(self, db):
        product = ProductFactory(
            name="Chanel No 5",
            category="Eau de Parfum",
            price=Decimal("149.99"),
            size="100ml",
        )
        assert product.pk is not None
        assert isinstance(product.id, uuid.UUID)

    def test_product_str_returns_name(self, db):
        product = ProductFactory(name="Dior Sauvage")
        assert str(product) == "Dior Sauvage"

    def test_product_id_is_uuid(self, db):
        product = ProductFactory()
        assert isinstance(product.id, uuid.UUID)

    def test_product_id_is_not_editable(self):
        field = Product._meta.get_field("id")
        assert field.editable is False

    def test_product_timestamps_set_on_creation(self, db):
        before = timezone.now()
        product = ProductFactory()
        after = timezone.now()
        assert before <= product.created_at <= after

    def test_product_updated_at_changes_on_save(self, db):
        product = ProductFactory()
        old = product.updated_at
        product.name = "Nouveau nom"
        product.save()
        product.refresh_from_db()
        assert product.updated_at >= old

    def test_product_category_choices(self, db):
        valid_categories = ["Eau de Parfum", "Eau de Toilette", "Extrait de Parfum"]
        for cat in valid_categories:
            p = ProductFactory(category=cat)
            assert p.category == cat

    def test_product_family_choices(self, db):
        valid_families = ["Floral", "Boisé", "Oriental", "Fruité", "Aromatique"]
        for fam in valid_families:
            p = ProductFactory(family=fam)
            assert p.family == fam

    def test_product_gender_choices(self, db):
        for gender in ["Homme", "Femme", "Unisexe"]:
            p = ProductFactory(gender=gender)
            assert p.gender == gender

    def test_product_optional_fields_blank_by_default(self, db):
        product = Product.objects.create(
            name="Test",
            category="Eau de Parfum",
            price=Decimal("50.00"),
            size="50ml",
            image="https://example.com/img.jpg",
            family="Floral",
            gender="Unisexe",
        )
        assert product.badge is None
        assert product.notes_top == ""
        assert product.notes_heart == ""
        assert product.notes_base == ""
        assert product.composition == ""
        assert product.advice == ""

    def test_product_price_precision(self, db):
        product = ProductFactory(price=Decimal("99.99"))
        product.refresh_from_db()
        assert product.price == Decimal("99.99")

    def test_product_name_max_length(self):
        field = Product._meta.get_field("name")
        assert field.max_length == 150