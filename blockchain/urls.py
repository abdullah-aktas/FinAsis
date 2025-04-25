"""
Blockchain Modülü - URL Yapılandırması
------------------------------------
Bu dosya, Blockchain modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v2/blockchain/ - Ana blockchain API endpoint'i
- /api/v2/blockchain/transactions/ - Blockchain işlemleri
- /api/v2/blockchain/wallets/ - Cüzdan yönetimi
- /api/v2/blockchain/smart-contracts/ - Akıllı kontratlar
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blockchain'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'wallets', views.WalletViewSet, basename='wallet')
router.register(r'smart-contracts', views.SmartContractViewSet, basename='smart-contract')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Blockchain İşlemleri
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/<uuid:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction-update'),
    path('transactions/<uuid:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    
    # Cüzdan Yönetimi
    path('wallets/', views.WalletListView.as_view(), name='wallet-list'),
    path('wallets/<uuid:pk>/', views.WalletDetailView.as_view(), name='wallet-detail'),
    path('wallets/create/', views.WalletCreateView.as_view(), name='wallet-create'),
    path('wallets/<uuid:pk>/update/', views.WalletUpdateView.as_view(), name='wallet-update'),
    path('wallets/<uuid:pk>/delete/', views.WalletDeleteView.as_view(), name='wallet-delete'),
    
    # Akıllı Kontratlar
    path('smart-contracts/', views.SmartContractListView.as_view(), name='smart-contract-list'),
    path('smart-contracts/<uuid:pk>/', views.SmartContractDetailView.as_view(), name='smart-contract-detail'),
    path('smart-contracts/create/', views.SmartContractCreateView.as_view(), name='smart-contract-create'),
    path('smart-contracts/<uuid:pk>/update/', views.SmartContractUpdateView.as_view(), name='smart-contract-update'),
    path('smart-contracts/<uuid:pk>/delete/', views.SmartContractDeleteView.as_view(), name='smart-contract-delete'),
    
    # Blockchain Araçları
    path('tools/verify/', views.VerifyView.as_view(), name='verify'),
    path('tools/deploy/', views.DeployView.as_view(), name='deploy'),
    path('tools/interact/', views.InteractView.as_view(), name='interact'),
] 