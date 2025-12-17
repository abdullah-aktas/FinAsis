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
    ClientDashboardView,
)
from ..views.marketplace_frontend_views import (
    consultant_list,
    consultant_detail,
    booking_create,
    booking_detail,
)

app_name = "marketplace"

# API Router
router = DefaultRouter()
router.register(r"consultants", ConsultantProfileViewSet, basename="consultant")
router.register(r"services", ConsultantServiceViewSet, basename="service")
router.register(r"bookings", ConsultationBookingViewSet, basename="booking")
router.register(r"payments", ConsultationPaymentViewSet, basename="payment")
router.register(r"contracts", ConsultantContractViewSet, basename="contract")
router.register(r"reviews", ConsultantReviewViewSet, basename="review")
router.register(r"availability", ConsultantAvailabilityViewSet, basename="availability")

urlpatterns = [
    # Frontend views
    path("", consultant_list, name="consultant-list"),
    path(
        "consultants/<int:consultant_id>/", consultant_detail, name="consultant-detail"
    ),
    path(
        "consultants/<int:consultant_id>/book/", booking_create, name="booking-create"
    ),
    path("bookings/<int:booking_id>/", booking_detail, name="booking-detail"),
    # API endpoints
    path("api/", include(router.urls)),
    # Dashboard endpoints
    path(
        "api/consultant/dashboard/stats/",
        ConsultantDashboardView.as_view({"get": "stats"}),
        name="consultant-dashboard",
    ),
    path(
        "api/client/dashboard/stats/",
        ClientDashboardView.as_view({"get": "stats"}),
        name="client-dashboard",
    ),
]
