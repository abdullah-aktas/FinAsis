from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'production-orders', views.ProductionOrderViewSet)
router.register(r'quality-controls', views.QualityControlViewSet)
router.register(r'bill-of-materials', views.BillOfMaterialsViewSet)

app_name = 'virtual_company'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('competitors/', views.competitors, name='competitors'),
    path('api/', include(router.urls)),
] 