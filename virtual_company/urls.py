# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VirtualCompanyViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'companies', VirtualCompanyViewSet, basename='company')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
] 