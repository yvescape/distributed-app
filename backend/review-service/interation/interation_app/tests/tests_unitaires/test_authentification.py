"""
Tests unitaires — JWTUser et authentification custom.
"""
import uuid

import pytest

from interation_app.utils.authentication import JWTUser
from interation_app.tests.conftest import USER_ID, USER_EMAIL


pytestmark = pytest.mark.unit


class TestJWTUser:

    def test_attributes(self):
        user = JWTUser(user_id=USER_ID, email=USER_EMAIL, is_staff=False)
        assert user.id == USER_ID
        assert user.pk == USER_ID
        assert user.email == USER_EMAIL
        assert user.is_staff is False
        assert user.is_active is True

    def test_is_authenticated(self):
        user = JWTUser(user_id=USER_ID)
        assert user.is_authenticated is True

    def test_is_not_anonymous(self):
        user = JWTUser(user_id=USER_ID)
        assert user.is_anonymous is False

    def test_staff_flag(self):
        user = JWTUser(user_id=USER_ID, is_staff=True)
        assert user.is_staff is True

    def test_default_email_empty(self):
        user = JWTUser(user_id=USER_ID)
        assert user.email == ""