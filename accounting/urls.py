"""
Accounting Modülü - URL Yapılandırması
-------------------------------------
Bu dosya, muhasebe modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/accounting/ - Ana muhasebe API endpoint'i
- /api/v1/accounting/transactions/ - Muhasebe işlemleri
- /api/v1/accounting/accounts/ - Hesap yönetimi
- /api/v1/accounting/reports/ - Muhasebe raporları
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounting'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'transactions', views.AccountingTransactionViewSet, basename='transaction')
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'journals', views.JournalViewSet, basename='journal')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # Muhasebe İşlemleri
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/<uuid:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction-update'),
    path('transactions/<uuid:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    
    # Hesap Yönetimi
    path('accounts/', views.AccountListView.as_view(), name='account-list'),
    path('accounts/<uuid:pk>/', views.AccountDetailView.as_view(), name='account-detail'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='account-create'),
    path('accounts/<uuid:pk>/update/', views.AccountUpdateView.as_view(), name='account-update'),
    path('accounts/<uuid:pk>/delete/', views.AccountDeleteView.as_view(), name='account-delete'),
    
    # Muhasebe Raporları
    path('reports/balance-sheet/', views.BalanceSheetView.as_view(), name='balance-sheet'),
    path('reports/income-statement/', views.IncomeStatementView.as_view(), name='income-statement'),
    path('reports/cash-flow/', views.CashFlowView.as_view(), name='cash-flow'),
    path('reports/trial-balance/', views.TrialBalanceView.as_view(), name='trial-balance'),
    path('reports/general-ledger/', views.GeneralLedgerView.as_view(), name='general-ledger'),
] 