from rest_framework import viewsets, permissions
from src.apps.accounts.models import CustomUser
from src.apps.accounts.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] 