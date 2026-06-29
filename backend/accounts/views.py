"""Account views."""

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RoleTokenObtainPairSerializer


class RoleTokenObtainPairView(TokenObtainPairView):
    """Login endpoint for issues tokens carrying the role claim"""

    serializer_class = RoleTokenObtainPairSerializer
