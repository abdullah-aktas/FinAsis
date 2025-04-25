"""
Finans Modülü - URL Yapılandırması
----------------------------------
Bu dosya, Finans modülünün URL yapılandırmasını içerir.

URL Yapısı:
- /api/v1/finance/ - Ana finans API endpoint'i
- /api/v1/finance/transactions/ - İşlem yönetimi
- /api/v1/finance/budgets/ - Bütçe yönetimi
- /api/v1/finance/reports/ - Finansal raporlar
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'finance'

# API Router tanımlaması
router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'reports', views.FinancialReportViewSet, basename='report')

urlpatterns = [
    # API Endpoint'leri
    path('', include(router.urls)),
    
    # İşlem Yönetimi
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/<uuid:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction-update'),
    path('transactions/<uuid:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    
    # Bütçe Yönetimi
    path('budgets/', views.BudgetListView.as_view(), name='budget-list'),
    path('budgets/<uuid:pk>/', views.BudgetDetailView.as_view(), name='budget-detail'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget-create'),
    path('budgets/<uuid:pk>/update/', views.BudgetUpdateView.as_view(), name='budget-update'),
    path('budgets/<uuid:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget-delete'),
    
    # Finansal Raporlar
    path('reports/balance-sheet/', views.BalanceSheetView.as_view(), name='balance-sheet'),
    path('reports/income-statement/', views.IncomeStatementView.as_view(), name='income-statement'),
    path('reports/cash-flow/', views.CashFlowView.as_view(), name='cash-flow'),
    path('reports/custom/', views.CustomReportView.as_view(), name='custom-report'),
] 