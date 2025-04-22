from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'networks', views.BlockchainNetworkViewSet, basename='network')
router.register(r'contracts', views.SmartContractViewSet, basename='contract')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'wallets', views.WalletViewSet, basename='wallet')
router.register(r'tokens', views.TokenViewSet, basename='token')

urlpatterns = [
    path('api/', include(router.urls)),
] 