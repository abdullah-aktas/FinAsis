from django.urls import path, include
from . import views
from .views_extra import report_views
from .api import (
    InvoiceViewSet, ExpenseViewSet, BankTransactionViewSet,
    CompanyViewSet, CustomerViewSet, ProductViewSet, SaleViewSet, PaymentViewSet, BankAccountViewSet, InvoiceItemViewSet,
    webhook_receiver, sync_data, ai_suggest_entry, ai_analyze_finance, award_user_badge, level_up_user,
    export_summary_pdf, export_summary_excel, export_summary_json, export_summary_xml
)
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

app_name = 'accounting'

router = DefaultRouter()
router.register(r'api/invoices', InvoiceViewSet, basename='api_invoices')
router.register(r'api/expenses', ExpenseViewSet, basename='api_expenses')
router.register(r'api/banktransactions', BankTransactionViewSet, basename='api_banktransactions')
router.register(r'api/companies', CompanyViewSet, basename='api_companies')
router.register(r'api/customers', CustomerViewSet, basename='api_customers')
router.register(r'api/products', ProductViewSet, basename='api_products')
router.register(r'api/sales', SaleViewSet, basename='api_sales')
router.register(r'api/payments', PaymentViewSet, basename='api_payments')
router.register(r'api/bankaccounts', BankAccountViewSet, basename='api_bankaccounts')
router.register(r'api/invoiceitems', InvoiceItemViewSet, basename='api_invoiceitems')

schema_view = get_schema_view(
    openapi.Info(
        title="FinAsis Accounting API",
        default_version='v1',
        description="FinAsis fatura, gider ve banka işlemleri API dokümantasyonu",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Ana Sayfa
    path('', views.index, name='home'),
    path('home/', views.home, name='accounting_home'),
    
    # Company CRUD
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/update/', views.company_update, name='company_update'),
    path('companies/<int:pk>/delete/', views.company_delete, name='company_delete'),
    path('companies/<int:pk>/pdf/', views.company_pdf, name='company_pdf'),
    path('companies/<int:pk>/ai-summary/', views.company_ai_summary, name='company_ai_summary'),

    # Customer CRUD
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Invoice CRUD
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:pk>/send-gib/', views.invoice_send_gib, name='invoice_send_gib'),
    path('invoices/<int:pk>/check-gib/', views.invoice_check_gib_status, name='invoice_check_gib_status'),
    path('invoices/<int:pk>/cancel-gib/', views.invoice_cancel_gib, name='invoice_cancel_gib'),

    # Expense CRUD
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/update/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # Product CRUD
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Sale CRUD
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/update/', views.sale_update, name='sale_update'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale_delete'),

    # Payment CRUD
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/update/', views.payment_update, name='payment_update'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),

    # BankAccount CRUD
    path('bankaccounts/', views.bankaccount_list, name='bankaccount_list'),
    path('bankaccounts/create/', views.bankaccount_create, name='bankaccount_create'),
    path('bankaccounts/<int:pk>/', views.bankaccount_detail, name='bankaccount_detail'),
    path('bankaccounts/<int:pk>/update/', views.bankaccount_update, name='bankaccount_update'),
    path('bankaccounts/<int:pk>/delete/', views.bankaccount_delete, name='bankaccount_delete'),

    # BankTransaction CRUD
    path('banktransactions/', views.banktransaction_list, name='banktransaction_list'),
    path('banktransactions/create/', views.banktransaction_create, name='banktransaction_create'),
    path('banktransactions/<int:pk>/', views.banktransaction_detail, name='banktransaction_detail'),
    path('banktransactions/<int:pk>/update/', views.banktransaction_update, name='banktransaction_update'),
    path('banktransactions/<int:pk>/delete/', views.banktransaction_delete, name='banktransaction_delete'),

    # Rapor Görünümleri
    path('report/', views.report_redirect, name='report_redirect'),
    path('report/summary/', views.summary_report, name='summary_report'),
    path('report/chart/', views.income_expense_chart_data, name='chart_data'),
    path('report/dashboard/', views.chart_dashboard, name='dashboard'),
    path('report/summary-pdf/', views.summary_report_pdf, name='summary_report_pdf'),

    # API
    path('', include(router.urls)),
    path('api/webhook/', webhook_receiver, name='api_webhook'),
    path('api/sync/', sync_data, name='api_sync'),
    path('api/ai/suggest-entry/', ai_suggest_entry, name='api_ai_suggest_entry'),
    path('api/ai/analyze-finance/', ai_analyze_finance, name='api_ai_analyze_finance'),
    path('api/gamification/award-badge/', award_user_badge, name='api_gamification_award_badge'),
    path('api/gamification/level-up/', level_up_user, name='api_gamification_level_up'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api_redoc'),
    path('api/export/summary/pdf/', export_summary_pdf, name='api_export_summary_pdf'),
    path('api/export/summary/excel/', export_summary_excel, name='api_export_summary_excel'),
    path('api/export/summary/json/', export_summary_json, name='api_export_summary_json'),
    path('api/export/summary/xml/', export_summary_xml, name='api_export_summary_xml'),
    # EDefter işlemleri
    path('edefter/<int:pk>/send-gib/', views.edefter_send_gib, name='edefter_send_gib'),
    path('edefter/<int:pk>/get-berat/', views.edefter_get_berat, name='edefter_get_berat'),
    # Beyanname raporları
    path('declarations/', report_views.declaration_report_list, name='declaration_report_list'),
    path('declarations/kdv/', report_views.kdv_report_view, name='kdv_report'),
    path('declarations/muhtasar/', report_views.muhtasar_report_view, name='muhtasar_report'),
    path('declarations/babs/', report_views.babs_report_view, name='babs_report'),
    # Resmi defterler
    path('defter/yevmiye/', report_views.yevmiye_defteri_view, name='yevmiye_defteri'),
    path('defter/kebir/', report_views.kebir_defteri_view, name='kebir_defteri'),
    path('defter/mizan/', report_views.mizan_defteri_view, name='mizan_defteri'),
    # Diğer zorunlu defter ve finansal tablolar
    path('defter/envanter/', report_views.envanter_defteri_view, name='envanter_defteri'),
    path('defter/kasa/', report_views.kasa_defteri_view, name='kasa_defteri'),
    path('defter/demirbas/', report_views.demirbas_defteri_view, name='demirbas_defteri'),
    path('finansal/bilanco/', report_views.bilanco_view, name='bilanco'),
    path('finansal/gelir-tablosu/', report_views.gelir_tablosu_view, name='gelir_tablosu'),
    path('finansal/nakit-akisi/', report_views.nakit_akisi_tablosu_view, name='nakit_akisi_tablosu'),
    # Finansal analiz ve AI öneriler
    path('finansal/analiz/', report_views.financial_analysis_view, name='financial_analysis'),
]
