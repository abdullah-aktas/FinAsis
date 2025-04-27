"""
Finance Modülü - URL Yapılandırması
---------------------
Bu dosya, Finance modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/finance/ - Ana finans API endpoint'i
- /api/v1/finance/transactions/ - İşlem yönetimi
- /api/v1/finance/budgets/ - Bütçe yönetimi
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, BudgetViewSet

app_name = 'finance'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
] 