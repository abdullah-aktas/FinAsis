from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'e-invoices', views.EInvoiceViewSet)
router.register(r'e-archive', views.EArchiveViewSet)
router.register(r'bank-integrations', views.BankIntegrationViewSet)

app_name = 'integrations'

urlpatterns = [
    path('', include(router.urls)),
] 