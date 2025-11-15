# -*- coding: utf-8 -*-
"""
Mali Müşavir Marketplace URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..views.marketplace_views import (
    ConsultantProfileViewSet,
    ConsultantServiceViewSet,
    ConsultationBookingViewSet,
    ConsultationPaymentViewSet,
    ConsultantContractViewSet,
    ConsultantReviewViewSet,
    ConsultantAvailabilityViewSet,
    ConsultantDashboardView,
    ClientDashboardView
)

app_name = 'marketplace'

# API Router
router = DefaultRouter()
router.register(r'consultants', ConsultantProfileViewSet, basename='consultant')
router.register(r'services', ConsultantServiceViewSet, basename='service')
router.register(r'bookings', ConsultationBookingViewSet, basename='booking')
router.register(r'payments', ConsultationPaymentViewSet, basename='payment')
router.register(r'contracts', ConsultantContractViewSet, basename='contract')
router.register(r'reviews', ConsultantReviewViewSet, basename='review')
router.register(r'availability', ConsultantAvailabilityViewSet, basename='availability')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Dashboard endpoints
    path('api/consultant/dashboard/stats/', 
         ConsultantDashboardView.as_view({'get': 'stats'}), 
         name='consultant-dashboard'),
    path('api/client/dashboard/stats/', 
         ClientDashboardView.as_view({'get': 'stats'}), 
         name='client-dashboard'),
]
