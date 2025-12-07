# -*- coding: utf-8 -*-
"""
Finance Banking URLs
Banka Entegrasyonu URL Yapılandırması
"""
from django.urls import path
from . import views

app_name = "finance_banking"

urlpatterns = [
    # Ana dashboard
    path("", views.banking_dashboard, name="dashboard"),
    # Hesap yönetimi
    path("accounts/", views.account_list, name="account_list"),
    # İşlem yönetimi
    path("transactions/", views.transaction_list, name="transaction_list"),
    # Mutabakat
    path("reconciliations/", views.reconciliation_list, name="reconciliation_list"),
    # Ödeme emirleri
    path("payment-orders/", views.payment_order_list, name="payment_order_list"),
    # AJAX endpoints
    path(
        "ajax/account-balance/<int:account_id>/",
        views.ajax_account_balance,
        name="ajax_account_balance",
    ),
    path(
        "ajax/sync-transactions/<int:account_id>/",
        views.ajax_sync_transactions,
        name="ajax_sync_transactions",
    ),
    path(
        "ajax/dashboard-stats/", views.ajax_dashboard_stats, name="ajax_dashboard_stats"
    ),
]
