# -*- coding: utf-8 -*-
"""
Finance uygulaması URL yapılandırmaları
"""

from django.urls import path, include
from FinAsis.apps.finance.home import finance_home
from .views import banking, einvoice, accounting, checks, download_financial_report
from .api.urls import urlpatterns as api_urlpatterns
from .urls.web_urls import urlpatterns as web_urlpatterns

app_name = 'finance'

urlpatterns = api_urlpatterns + web_urlpatterns

urlpatterns += [
    path('', finance_home, name='finance_home'),
    # Banka hesapları ve işlemler
    path('bank-accounts/', banking.BankAccountListView.as_view(), name='bank_accounts'),
    path('bank-accounts/<int:pk>/', banking.BankAccountDetailView.as_view(), name='bank_account_detail'),
    path('bank-accounts/create/', banking.BankAccountCreateView.as_view(), name='bank_account_create'),
    path('bank-accounts/<int:pk>/edit/', banking.BankAccountUpdateView.as_view(), name='bank_account_edit'),
    path('bank-accounts/<int:pk>/delete/', banking.BankAccountDeleteView.as_view(), name='bank_account_delete'),
    
    path('transactions/', banking.TransactionListView.as_view(), name='transactions'),
    path('transactions/<int:pk>/', banking.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/create/', banking.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/edit/', banking.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transactions/<int:pk>/delete/', banking.TransactionDeleteView.as_view(), name='transaction_delete'),
    
    path('bank-summary/', banking.bank_summary, name='bank_summary'),
    
    # E-Fatura ve E-Arşiv işlemleri
    path('einvoices/', einvoice.EInvoiceListView.as_view(), name='einvoice_list'),
    path('einvoices/<int:pk>/', einvoice.EInvoiceDetailView.as_view(), name='einvoice_detail'),
    path('einvoices/create/', einvoice.EInvoiceCreateView.as_view(), name='einvoice_create'),
    path('einvoices/<int:pk>/edit/', einvoice.EInvoiceUpdateView.as_view(), name='einvoice_edit'),
    path('einvoices/<int:pk>/delete/', einvoice.EInvoiceDeleteView.as_view(), name='einvoice_delete'),
    
    path('einvoices/<int:pk>/send/', einvoice.send_einvoice, name='einvoice_send'),
    path('einvoices/<int:pk>/download/', einvoice.download_einvoice, name='einvoice_download'),
    path('einvoices/<int:invoice_id>/items/add/', einvoice.add_invoice_item, name='einvoice_add_item'),
    path('einvoices/<int:invoice_id>/status/update/', einvoice.update_invoice_status, name='einvoice_update_status'),
    
    # Diğer finans işlemleri (örneğin muhasebe, çek/senet) urlpattern'leri buraya eklenecek

    # path('employee/', accounting.EmployeeListView.as_view(), name='employee_list'),
    # path('employee/<int:pk>/', accounting.EmployeeDetailView.as_view(), name='employee_detail'),
    # path('employee/create/', accounting.EmployeeCreateView.as_view(), name='employee_create'),
    # path('employee/<int:pk>/update/', accounting.EmployeeUpdateView.as_view(), name='employee_update'),
    # path('employee/<int:pk>/delete/', accounting.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('voucher/', accounting.VoucherListView.as_view(), name='voucher_list'),
    # path('voucher/<int:pk>/', accounting.VoucherDetailView.as_view(), name='voucher_detail'),
    path('voucher/create/', accounting.VoucherCreateView.as_view(), name='voucher_create'),
    # path('voucher/<int:pk>/update/', accounting.VoucherUpdateView.as_view(), name='voucher_update'),
    # path('voucher/<int:pk>/delete/', accounting.VoucherDeleteView.as_view(), name='voucher_delete'),
    path('report/pdf/', download_financial_report, name='download_financial_report'),
] 