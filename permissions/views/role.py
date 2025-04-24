from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from permissions.models import Role
from permissions.serializers import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    """
    Role modeli için ViewSet
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated] 