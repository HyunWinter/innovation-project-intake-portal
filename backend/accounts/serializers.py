"""Account serializers."""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT Login serializer w the role and name token"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["name"] = user.name
        return token
