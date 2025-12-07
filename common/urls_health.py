"""
Health Check URL Configuration
Public erişilebilir health check endpoint'leri
"""

from django.urls import path
from . import views_health

app_name = "health"

urlpatterns = [
    path("", views_health.health_check_simple, name="health_check"),
    path("detailed/", views_health.health_check_detailed, name="health_check_detailed"),
    path("status/", views_health.site_status, name="site_status"),
]
