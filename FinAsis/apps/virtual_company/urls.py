# -*- coding: utf-8 -*-
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import VirtualCompanyViewSet, ProductViewSet, ARAccountingEntryCreateAPIView, ARCompanyListAPIView, ARProductByMarkerAPIView

router = DefaultRouter()
router.register(r'companies', VirtualCompanyViewSet, basename='company')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('ar/accounting-entry/', ARAccountingEntryCreateAPIView.as_view(), name='ar_accounting_entry_create'),
    path('ar/companies/', ARCompanyListAPIView.as_view(), name='ar_company_list'),
    path('ar/product/marker/<str:marker_id>/', ARProductByMarkerAPIView.as_view(), name='ar_product_by_marker'),
] 