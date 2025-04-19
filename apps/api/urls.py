from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from rest_framework.routers import DefaultRouter

from apps.api.views import (
    RoleViewSet, FinanceAPIView, StockAPIView, 
    AccountingAPIView, ProductAPIView, InvoiceAPIView
)

app_name = 'api'

# ViewSet'ler için router
router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    # JWT Token endpointleri
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # Router URL'leri
    path('', include(router.urls)),
    
    # Modül bazlı API endpointleri
    path('finance/', FinanceAPIView.as_view(), name='finance'),
    path('stock/', StockAPIView.as_view(), name='stock'),
    path('accounting/', AccountingAPIView.as_view(), name='accounting'),
    path('products/', ProductAPIView.as_view(), name='products'),
    path('invoices/', InvoiceAPIView.as_view(), name='invoices'),
] 