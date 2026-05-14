# orders_app/utils/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTUser:
    """Objet User léger basé uniquement sur les claims JWT."""
    
    def __init__(self, user_id, is_staff=False):
        self.id = user_id
        self.pk = user_id
        self.is_staff = is_staff
        self.is_active = True
        self.username = user_id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class JWTAuthenticationWithoutDB(JWTAuthentication):

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if not user_id:
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()

        return JWTUser(
            user_id=user_id,
            is_staff=validated_token.get("is_staff", False),
        )