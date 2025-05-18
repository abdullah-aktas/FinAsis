# -*- coding: utf-8 -*-
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet,
    LeadViewSet,
    InteractionLogViewSet
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'interaction-logs', InteractionLogViewSet, basename='interaction-log')

urlpatterns = [
    path('', include(router.urls)),
] 