# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VirtualCompanyViewSet,
    ProductViewSet,
    ARAccountingEntryCreateAPIView,
    ARCompanyListAPIView,
    ARProductByMarkerAPIView,
    VirtualCompanyListView,
    VirtualCompanyDetailView,
    VirtualCompanyCreateView,
    VirtualCompanyUpdateView,
    VirtualCompanyDeleteView,
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

app_name = "virtual_company"

router = DefaultRouter()
router.register(r"companies", VirtualCompanyViewSet, basename="company")
router.register(r"products", ProductViewSet, basename="product")

api_patterns = [
    path("", include(router.urls)),
    path(
        "ar/accounting-entry/",
        ARAccountingEntryCreateAPIView.as_view(),
        name="ar_accounting_entry_create",
    ),
    path("ar/companies/", ARCompanyListAPIView.as_view(), name="ar_company_list"),
    path(
        "ar/product/marker/<str:marker_id>/",
        ARProductByMarkerAPIView.as_view(),
        name="ar_product_by_marker",
    ),
]

web_patterns = [
    path("", VirtualCompanyListView.as_view(), name="virtual_company_list"),
    path("create/", VirtualCompanyCreateView.as_view(), name="virtual_company_create"),
    path(
        "<int:pk>/", VirtualCompanyDetailView.as_view(), name="virtual_company_detail"
    ),
    path(
        "<int:pk>/update/",
        VirtualCompanyUpdateView.as_view(),
        name="virtual_company_update",
    ),
    path(
        "<int:pk>/delete/",
        VirtualCompanyDeleteView.as_view(),
        name="virtual_company_delete",
    ),
    # Product CRUD (scoped under a company via query param or selection later)
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path(
        "products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"
    ),
    path(
        "products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"
    ),
]

urlpatterns = web_patterns + [
    path("api/", include((api_patterns, "api"))),
]
