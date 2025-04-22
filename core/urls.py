from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthCheckViewSet, DashboardView, ErrorView

router = DefaultRouter()
router.register(r'health', HealthCheckViewSet, basename='health')

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/', include(router.urls)),
    path('error/<int:code>/<str:message>/', ErrorView.as_view(), name='error'),
] 