# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü - URL yapılandırması

Bu modül, muhasebe modülünün URL yapılandırmasını içerir.
"""
from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    # Ana sayfa
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Hesap Türleri
    path('account-types/', views.AccountTypeListView.as_view(), name='account_type_list'),
    path('account-types/<str:pk>/', views.AccountTypeDetailView.as_view(), name='account_type_detail'),
    path('account-types/create/', views.AccountTypeCreateView.as_view(), name='account_type_create'),
    path('account-types/<str:pk>/update/', views.AccountTypeUpdateView.as_view(), name='account_type_update'),
    path('account-types/<str:pk>/delete/', views.AccountTypeDeleteView.as_view(), name='account_type_delete'),
    
    # Hesaplar
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name='account_update'),
    path('accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    
    # Fiş Türleri
    path('voucher-types/', views.VoucherTypeListView.as_view(), name='voucher_type_list'),
    path('voucher-types/<str:pk>/', views.VoucherTypeDetailView.as_view(), name='voucher_type_detail'),
    path('voucher-types/create/', views.VoucherTypeCreateView.as_view(), name='voucher_type_create'),
    path('voucher-types/<str:pk>/update/', views.VoucherTypeUpdateView.as_view(), name='voucher_type_update'),
    path('voucher-types/<str:pk>/delete/', views.VoucherTypeDeleteView.as_view(), name='voucher_type_delete'),
    
    # Fişler
    path('vouchers/', views.VoucherListView.as_view(), name='voucher_list'),
    path('vouchers/<int:pk>/', views.VoucherDetailView.as_view(), name='voucher_detail'),
    path('vouchers/create/', views.VoucherCreateView.as_view(), name='voucher_create'),
    path('vouchers/<int:pk>/update/', views.VoucherUpdateView.as_view(), name='voucher_update'),
    path('vouchers/<int:pk>/delete/', views.VoucherDeleteView.as_view(), name='voucher_delete'),
    path('vouchers/<int:pk>/post/', views.post_voucher, name='post_voucher'),
    path('vouchers/<int:pk>/cancel/', views.cancel_voucher, name='cancel_voucher'),
    path('vouchers/<int:pk>/reverse/', views.create_reverse_voucher, name='create_reverse_voucher'),
    
    # Belge Yönetimi
    path('vouchers/<int:voucher_id>/documents/', views.VoucherDocumentListView.as_view(), name='voucher_document_list'),
    path('vouchers/<int:voucher_id>/documents/create/', views.VoucherDocumentCreateView.as_view(), name='voucher_document_create'),
    path('documents/<int:pk>/', views.VoucherDocumentDetailView.as_view(), name='voucher_document_detail'),
    path('documents/<int:pk>/delete/', views.VoucherDocumentDeleteView.as_view(), name='voucher_document_delete'),
    path('documents/<int:pk>/download/', views.voucher_document_download, name='voucher_document_download'),
    
    # Para Birimi ve Kur
    path('currencies/', views.CurrencyListView.as_view(), name='currency_list'),
    path('currencies/create/', views.CurrencyCreateView.as_view(), name='currency_create'),
    path('currencies/<str:pk>/', views.CurrencyDetailView.as_view(), name='currency_detail'),
    path('currencies/<str:pk>/update/', views.CurrencyUpdateView.as_view(), name='currency_update'),
    path('currencies/<str:pk>/delete/', views.CurrencyDeleteView.as_view(), name='currency_delete'),
    path('currencies/<str:pk>/set-default/', views.currency_set_default, name='currency_set_default'),
    
    path('exchange-rates/', views.ExchangeRateListView.as_view(), name='exchange_rate_list'),
    path('exchange-rates/create/', views.ExchangeRateCreateView.as_view(), name='exchange_rate_create'),
    path('exchange-rates/<int:pk>/', views.ExchangeRateDetailView.as_view(), name='exchange_rate_detail'),
    path('exchange-rates/<int:pk>/update/', views.ExchangeRateUpdateView.as_view(), name='exchange_rate_update'),
    path('exchange-rates/<int:pk>/delete/', views.ExchangeRateDeleteView.as_view(), name='exchange_rate_delete'),
    path('exchange-rates/import/', views.exchange_rate_import, name='exchange_rate_import'),
    
    # Finansal Raporlama
    path('reports/', views.FinancialReportListView.as_view(), name='financial_report_list'),
    path('reports/create/', views.FinancialReportCreateView.as_view(), name='financial_report_create'),
    path('reports/<int:pk>/', views.FinancialReportDetailView.as_view(), name='financial_report_detail'),
    path('reports/<int:pk>/update/', views.FinancialReportUpdateView.as_view(), name='financial_report_update'),
    path('reports/<int:pk>/delete/', views.FinancialReportDeleteView.as_view(), name='financial_report_delete'),
    path('reports/<int:pk>/generate/', views.financial_report_generate, name='financial_report_generate'),
    path('reports/<int:pk>/export/', views.financial_report_export, name='financial_report_export'),
    
    # Hazır Raporlar
    path('reports/trial-balance/', views.trial_balance_report, name='trial_balance_report'),
    path('reports/income-statement/', views.income_statement_report, name='income_statement_report'),
    path('reports/balance-sheet/', views.balance_sheet_report, name='balance_sheet_report'),
    path('reports/ledger/', views.general_ledger_report, name='general_ledger_report'),
    
    # Vergi Beyanname Yönetimi
    path('tax-declarations/', views.TaxDeclarationListView.as_view(), name='tax_declaration_list'),
    path('tax-declarations/create/', views.TaxDeclarationCreateView.as_view(), name='tax_declaration_create'),
    path('tax-declarations/<int:pk>/', views.TaxDeclarationDetailView.as_view(), name='tax_declaration_detail'),
    path('tax-declarations/<int:pk>/update/', views.TaxDeclarationUpdateView.as_view(), name='tax_declaration_update'),
    path('tax-declarations/<int:pk>/delete/', views.TaxDeclarationDeleteView.as_view(), name='tax_declaration_delete'),
    path('tax-declarations/<int:pk>/submit/', views.tax_declaration_submit, name='tax_declaration_submit'),
    path('tax-declarations/<int:pk>/accept/', views.tax_declaration_accept, name='tax_declaration_accept'),
    path('tax-declarations/<int:declaration_id>/files/create/', views.TaxDeclarationFileCreateView.as_view(), name='tax_declaration_file_create'),
    path('tax-declaration-files/<int:pk>/delete/', views.TaxDeclarationFileDeleteView.as_view(), name='tax_declaration_file_delete'),
    path('tax-declaration-files/<int:pk>/download/', views.tax_declaration_file_download, name='tax_declaration_file_download'),
    
    # Bütçe Yönetimi
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
    path('budgets/<int:pk>/activate/', views.budget_activate, name='budget_activate'),
    path('budgets/<int:pk>/close/', views.budget_close, name='budget_close'),
    path('budgets/<int:pk>/report/', views.budget_report, name='budget_report'),
] 