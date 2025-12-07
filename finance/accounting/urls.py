# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü - URL yapılandırması

Bu modül, muhasebe modülünün URL yapılandırmasını içerir.
"""
from django.urls import path
from . import views

app_name = "accounting"

urlpatterns = [
    # Ana sayfa
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Hesap Türleri
    path(
        "account-types/", views.AccountTypeListView.as_view(), name="account_type_list"
    ),
    path(
        "account-types/<str:pk>/",
        views.AccountTypeDetailView.as_view(),
        name="account_type_detail",
    ),
    path(
        "account-types/create/",
        views.AccountTypeCreateView.as_view(),
        name="account_type_create",
    ),
    path(
        "account-types/<str:pk>/update/",
        views.AccountTypeUpdateView.as_view(),
        name="account_type_update",
    ),
    path(
        "account-types/<str:pk>/delete/",
        views.AccountTypeDeleteView.as_view(),
        name="account_type_delete",
    ),
    # Hesaplar
    path("accounts/", views.AccountListView.as_view(), name="account_list"),
    path(
        "accounts/<int:pk>/", views.AccountDetailView.as_view(), name="account_detail"
    ),
    path("accounts/create/", views.AccountCreateView.as_view(), name="account_create"),
    path(
        "accounts/<int:pk>/update/",
        views.AccountUpdateView.as_view(),
        name="account_update",
    ),
    path(
        "accounts/<int:pk>/delete/",
        views.AccountDeleteView.as_view(),
        name="account_delete",
    ),
    # Fiş Türleri
    path(
        "voucher-types/", views.VoucherTypeListView.as_view(), name="voucher_type_list"
    ),
    path(
        "voucher-types/<str:pk>/",
        views.VoucherTypeDetailView.as_view(),
        name="voucher_type_detail",
    ),
    path(
        "voucher-types/create/",
        views.VoucherTypeCreateView.as_view(),
        name="voucher_type_create",
    ),
    path(
        "voucher-types/<str:pk>/update/",
        views.VoucherTypeUpdateView.as_view(),
        name="voucher_type_update",
    ),
    path(
        "voucher-types/<str:pk>/delete/",
        views.VoucherTypeDeleteView.as_view(),
        name="voucher_type_delete",
    ),
    # Fişler
    path("vouchers/", views.VoucherListView.as_view(), name="voucher_list"),
    path(
        "vouchers/<int:pk>/", views.VoucherDetailView.as_view(), name="voucher_detail"
    ),
    path("vouchers/create/", views.VoucherCreateView.as_view(), name="voucher_create"),
    path(
        "vouchers/<int:pk>/update/",
        views.VoucherUpdateView.as_view(),
        name="voucher_update",
    ),
    path(
        "vouchers/<int:pk>/delete/",
        views.VoucherDeleteView.as_view(),
        name="voucher_delete",
    ),
    path("vouchers/<int:pk>/post/", views.post_voucher, name="post_voucher"),
    path("vouchers/<int:pk>/cancel/", views.cancel_voucher, name="cancel_voucher"),
    path(
        "vouchers/<int:pk>/reverse/",
        views.create_reverse_voucher,
        name="create_reverse_voucher",
    ),
]
