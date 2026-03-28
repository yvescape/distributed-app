# tests/factories.py
import uuid
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from auth_app.models.user_profile import UserProfile
from auth_app.models.user_audit_log import UserAuditLog

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True  # on gère le save manuellement ci-dessous

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_email_verified = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        raw = extracted or "StrongPass123!"
        obj.set_password(raw)
        if create:
            obj.save(update_fields=["password"])  # save uniquement le champ password


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory)
    phone_number = factory.Faker("phone_number")
    bio = factory.Faker("sentence")
    country = factory.Faker("country")
    avatar = factory.LazyAttribute(lambda o: f"https://cdn.example.com/avatars/{o.user.username}.jpg")


class UserAuditLogFactory(DjangoModelFactory):
    class Meta:
        model = UserAuditLog

    user = factory.SubFactory(UserFactory)
    action = "LOGIN"
    ip_address = factory.Faker("ipv4")