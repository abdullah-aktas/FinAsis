# -*- coding: utf-8 -*-
"""
Security & Compliance Application URL Configuration
"""

from django.urls import path
from .views.compliance_views import *

app_name = "security"

urlpatterns = [
    # Ana compliance dashboard
    path("", compliance_dashboard, name="compliance_dashboard"),
    # Kişi hakları talepleri
    path("data-requests/", data_subject_requests, name="data_subject_requests"),
    # Kişisel veri envanteri
    path("data-inventory/", personal_data_inventory, name="personal_data_inventory"),
    # Güvenlik olayları
    path("incidents/", security_incidents, name="security_incidents"),
    # Veri yedekleme
    path("backup/", data_backup_management, name="data_backup"),
    # Şifreleme yönetimi
    path("encryption/", encryption_management, name="encryption_management"),
    # AJAX endpoints
    path("ajax/compliance-check/", ajax_compliance_check, name="ajax_compliance_check"),
    path("ajax/security-metrics/", ajax_security_metrics, name="ajax_security_metrics"),
]
