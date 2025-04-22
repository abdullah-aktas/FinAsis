"""
Rol tabanlı yetkilendirme örneği olacak API görünümleri.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle, ScopedRateThrottle

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from permissions.permissions import (
    IsAdmin, IsFinanceManager, IsStockOperator, 
    IsAccountingStaff, IsSalesStaff, ActionBasedPermission, ModulePermission
)
from permissions.models import Role, Permission, UserRole
from .serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer

User = get_user_model()


class RoleViewSet(viewsets.ModelViewSet):
    """
    Rolleri listelemek, oluşturmak, güncellemek ve silmek için API endpoint.
    
    Erişim izni:
    - Admin kullanıcılar tüm işlemleri yapabilir.
    - Diğer kullanıcılar sadece rolleri listeleyebilir ve detaylarını görebilir.
    """
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        'list': ['admin', 'manager', 'finance_manager', 'accounting', 'stock_operator', 'sales', 'hr'],
        'retrieve': ['admin', 'manager', 'finance_manager', 'accounting', 'stock_operator', 'sales', 'hr'],
        'create': ['admin'],
        'update': ['admin'],
        'partial_update': ['admin'],
        'destroy': ['admin'],
        'assign_to_user': ['admin', 'manager'],
        'remove_from_user': ['admin', 'manager'],
    }
    
    # Burada normalde serializer ve queryset tanımlamaları olacak
    # Örnek amaçlı olduğu için şimdilik geçiyoruz
    
    @action(detail=True, methods=['post'])
    def assign_to_user(self, request, pk=None):
        """Bir rolü bir kullanıcıya atar."""
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id alanı gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Kullanıcı bulunamadı."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Kullanıcı-rol ilişkisi oluştur veya güncelle
        user_role, created = UserRole.objects.update_or_create(
            user=user,
            role=role,
            defaults={
                'assigned_by': request.user,
                'is_primary': request.data.get('is_primary', False)
            }
        )
        
        return Response(
            {"success": f"{user.username} kullanıcısına {role.name} rolü atandı."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def remove_from_user(self, request, pk=None):
        """Bir kullanıcıdan rol kaldırır."""
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id alanı gereklidir."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Kullanıcı bulunamadı."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Kullanıcı-rol ilişkisini kaldır
        deleted, _ = UserRole.objects.filter(user=user, role=role).delete()
        
        if deleted:
            return Response(
                {"success": f"{user.username} kullanıcısından {role.name} rolü kaldırıldı."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": f"{user.username} kullanıcısında {role.name} rolü bulunamadı."},
                status=status.HTTP_404_NOT_FOUND
            )


class FinanceAPIView(APIView):
    """
    Finans modülü için API endpoint örneği.
    Sadece finans yöneticileri ve admin kullanıcılar erişebilir.
    """
    permission_classes = [IsFinanceManager]
    
    def get(self, request, format=None):
        """Finans verilerini listeler."""
        return Response({
            "message": "Finans modülüne erişim sağlandı.",
            "user": request.user.username,
            "role": request.user.role
        })


class StockAPIView(APIView):
    """
    Stok modülü için API endpoint örneği.
    Sadece depo yetkilileri ve admin kullanıcılar erişebilir.
    """
    permission_classes = [IsStockOperator]
    
    def get(self, request, format=None):
        """Stok verilerini listeler."""
        return Response({
            "message": "Stok modülüne erişim sağlandı.",
            "user": request.user.username,
            "role": request.user.role
        })


class AccountingAPIView(APIView):
    """
    Muhasebe modülü için API endpoint örneği.
    Sadece muhasebe personeli ve admin kullanıcılar erişebilir.
    """
    permission_classes = [IsAccountingStaff]
    
    def get(self, request, format=None):
        """Muhasebe verilerini listeler."""
        return Response({
            "message": "Muhasebe modülüne erişim sağlandı.",
            "user": request.user.username,
            "role": request.user.role
        })


class ProductAPIView(APIView):
    """
    Ürün modülü için API endpoint örneği.
    ModulePermission kullanarak izinleri kontrol eder.
    """
    permission_classes = [ModulePermission]
    module_name = 'stock'
    
    def get(self, request, format=None):
        """Ürünleri listeler."""
        return Response({
            "message": "Ürün verilerine erişim sağlandı.",
            "user": request.user.username,
            "role": request.user.role
        })
    
    def post(self, request, format=None):
        """Yeni ürün oluşturur."""
        return Response({
            "message": "Yeni ürün oluşturuldu.",
            "user": request.user.username,
            "role": request.user.role
        }, status=status.HTTP_201_CREATED)


class InvoiceAPIView(APIView):
    """
    Fatura modülü için API endpoint örneği.
    ModulePermission kullanarak izinleri kontrol eder.
    """
    permission_classes = [ModulePermission]
    module_name = 'finance'
    
    def get(self, request, format=None):
        """Faturaları listeler."""
        return Response({
            "message": "Fatura verilerine erişim sağlandı.",
            "user": request.user.username,
            "role": request.user.role
        })
    
    def post(self, request, format=None):
        """Yeni fatura oluşturur."""
        return Response({
            "message": "Yeni fatura oluşturuldu.",
            "user": request.user.username,
            "role": request.user.role
        }, status=status.HTTP_201_CREATED)


# Özel token throttle sınıfları
class TokenObtainThrottle(ScopedRateThrottle):
    scope = 'token_obtain'

class TokenRefreshThrottle(ScopedRateThrottle):
    scope = 'token_refresh'


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Özelleştirilmiş token alma view'ı. 
    
    Bu view, rate limiting uygular ve kullanıcı tipine göre 
    farklı token süreleri sağlar.
    """
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [TokenObtainThrottle]


class CustomTokenRefreshView(TokenRefreshView):
    """
    Özelleştirilmiş token yenileme view'ı.
    
    Bu view, rate limiting uygular ve eski token'ları blacklist'e ekler.
    """
    serializer_class = CustomTokenRefreshSerializer
    throttle_classes = [TokenRefreshThrottle] 