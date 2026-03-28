# products_app/tests/factories.py
import uuid
import factory
from factory.django import DjangoModelFactory
from products_app.models.product import Product


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
        skip_postgeneration_save = True

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Parfum Test {n}")
    category = "Eau de Parfum"
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    size = "100ml"
    image = factory.LazyAttribute(lambda o: f"https://cdn.example.com/{o.name}.jpg")
    badge = None

    family = "Floral"
    gender = "Unisexe"

    notes_top = "Bergamote, Citron"
    notes_heart = "Jasmin, Rose"
    notes_base = "Musc blanc, Santal"

    composition = "Alcohol, Aqua, Parfum"
    advice = "Vaporiser sur les poignets et le cou."