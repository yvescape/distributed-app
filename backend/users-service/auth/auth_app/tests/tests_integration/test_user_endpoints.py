# tests/integration/test_user_endpoints.py
import pytest
from auth_app.models.user_audit_log import UserAuditLog
from ..factories import UserFactory, UserProfileFactory


ME_URL = "/api/users/me/"
UPDATE_URL = "/api/users/update/"
PROFILE_URL = "/api/users/profile/"


@pytest.mark.integration
@pytest.mark.django_db
class TestMeEndpoint:

    def test_me_authenticated_returns_200(self, auth_client, user):
        response = auth_client.get(ME_URL)
        assert response.status_code == 200

    def test_me_returns_own_user_data(self, auth_client, user):
        response = auth_client.get(ME_URL)
        assert response.data["email"] == user.email
        assert response.data["username"] == user.username

    def test_me_returns_nested_profile(self, auth_client, user):
        response = auth_client.get(ME_URL)
        assert "profile" in response.data
        assert response.data["profile"] is not None

    def test_me_unauthenticated_returns_401(self, api_client):
        response = api_client.get(ME_URL)
        assert response.status_code == 401

    def test_me_does_not_expose_password(self, auth_client):
        response = auth_client.get(ME_URL)
        assert "password" not in response.data

    def test_me_contains_expected_fields(self, auth_client):
        response = auth_client.get(ME_URL)
        expected = {"id", "email", "username", "first_name", "last_name",
                    "is_active", "is_email_verified", "created_at", "profile"}
        assert expected.issubset(set(response.data.keys()))


@pytest.mark.integration
@pytest.mark.django_db
class TestUpdateUserEndpoint:
    """
    Tests pour PATCH/PUT /api/users/update/
    (UpdateUserView avec UpdateUserSerializer — first_name, last_name uniquement)
    """

    def test_update_first_name_returns_200(self, auth_client):
        response = auth_client.patch(UPDATE_URL, data={"first_name": "Updated", "last_name": "User"}, format="json")
        assert response.status_code == 200

    def test_update_persists_new_first_name(self, auth_client, user):
        auth_client.patch(UPDATE_URL, data={"first_name": "NewFirst", "last_name": "NewLast"}, format="json")
        user.refresh_from_db()
        assert user.first_name == "NewFirst"

    def test_update_creates_audit_log(self, auth_client, user):
        auth_client.patch(UPDATE_URL, data={"first_name": "X", "last_name": "Y"}, format="json")
        assert UserAuditLog.objects.filter(user=user, action="UPDATE").exists()

    def test_update_unauthenticated_returns_401(self, api_client):
        response = api_client.patch(UPDATE_URL, data={"first_name": "X", "last_name": "Y"}, format="json")
        assert response.status_code == 401

    def test_update_email_ignored(self, auth_client, user):
        """L'email ne doit pas être modifiable via cet endpoint."""
        original_email = user.email
        auth_client.patch(UPDATE_URL, data={"first_name": "X", "last_name": "Y", "email": "hacked@example.com"}, format="json")
        user.refresh_from_db()
        assert user.email == original_email

    def test_update_only_own_user(self, auth_client, user, db):
        """Chaque utilisateur ne peut modifier que son propre compte."""
        other_user = UserFactory(first_name="Other")
        auth_client.patch(UPDATE_URL, data={"first_name": "Injected", "last_name": "Name"}, format="json")
        other_user.refresh_from_db()
        assert other_user.first_name == "Other"


@pytest.mark.integration
@pytest.mark.django_db
class TestUpdateProfileEndpoint:

    def test_update_profile_returns_200(self, auth_client):
        response = auth_client.patch(PROFILE_URL, data={"bio": "Je suis dev Django"}, format="json")
        assert response.status_code == 200

    def test_update_profile_persists(self, auth_client, user):
        auth_client.patch(PROFILE_URL, data={"bio": "New bio", "country": "CI"}, format="json")
        user.profile.refresh_from_db()
        assert user.profile.bio == "New bio"
        assert user.profile.country == "CI"

    def test_update_profile_unauthenticated_returns_401(self, api_client):
        response = api_client.patch(PROFILE_URL, data={"bio": "test"}, format="json")
        assert response.status_code == 401

    def test_update_profile_partial_update(self, auth_client, user):
        """PATCH ne doit modifier que les champs fournis."""
        user.profile.country = "Sénégal"
        user.profile.save()
        auth_client.patch(PROFILE_URL, data={"bio": "Développeur"}, format="json")
        user.profile.refresh_from_db()
        assert user.profile.country == "Sénégal"  # non modifié
        assert user.profile.bio == "Développeur"

    def test_update_profile_creates_profile_if_missing(self, auth_client, user):
        """get_or_create dans la vue — ne doit pas lever d'erreur même sans profil."""
        from auth_app.models.user_profile import UserProfile
        UserProfile.objects.filter(user=user).delete()
        response = auth_client.patch(PROFILE_URL, data={"bio": "Créé à la volée"}, format="json")
        assert response.status_code in (200, 201)

    def test_update_profile_avatar_url(self, auth_client):
        response = auth_client.patch(
            PROFILE_URL,
            data={"avatar": "https://cdn.example.com/photo.jpg"},
            format="json"
        )
        assert response.status_code == 200
        assert response.data["avatar"] == "https://cdn.example.com/photo.jpg"