# -*- coding: utf-8 -*-
"""
API kullanıcı görünümleri
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView as JWTTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as JWTTokenRefreshView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from api.serializers.user_serializers import UserSerializer, CustomTokenObtainPairSerializer

class TokenObtainPairView(JWTTokenObtainPairView):
    """Özelleştirilmiş token edinme görünümü"""
    serializer_class = CustomTokenObtainPairSerializer

class TokenRefreshView(JWTTokenRefreshView):
    """Token yenileme görünümü"""
    pass

class UserViewSet(viewsets.ModelViewSet):
    """
    Kullanıcı API görünümü
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Kullanıcının erişim izni olan kullanıcıları filtrele"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Mevcut kullanıcının bilgilerini döndür"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Kullanıcı istatistiklerini döndür (yalnızca adminler için)"""
        if not request.user.is_staff:
            return Response({"detail": _("Bu bilgilere erişim izniniz yok.")}, status=403)
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        return Response({
            "total_users": total_users,
            "active_users": active_users,
            "staff_users": staff_users,
        }) 