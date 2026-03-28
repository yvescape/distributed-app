# products_app/tests/conftest.py
import pytest
from rest_framework.test import APIClient
from .factories import ProductFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product(db):
    return ProductFactory()


@pytest.fixture
def products(db):
    return ProductFactory.create_batch(5)