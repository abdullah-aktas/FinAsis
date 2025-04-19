from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

from .views import CustomTokenObtainPairView

# Swagger/OpenAPI şema görünümü
schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis API",
        default_version='v1',
        description="FinAsis finansal yönetim sistemi API dokümantasyonu",
        terms_of_service="https://www.finasis.com/terms/",
        contact=openapi.Contact(email="contact@finasis.com"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=[],
)

urlpatterns = [
    # Kimlik doğrulama
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API modülleri
    path('finance/', include('apps.api.finance.urls')),
    path('crm/', include('apps.api.crm.urls')),
    path('accounting/', include('apps.api.accounting.urls')),
    
    # API dokümantasyonu
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 