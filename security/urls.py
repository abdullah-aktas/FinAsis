# -*- coding: utf-8 -*-
"""
Security & Compliance Application URL Configuration
"""

from django.urls import path
from .views.compliance_views import *  # noqa: F403, F405

app_name = "security"

urlpatterns = [
    # Ana compliance dashboard
    path("", compliance_dashboard, name="compliance_dashboard"),  # noqa: F405
    # Kişi hakları talepleri
    path(
        "data-requests/", data_subject_requests, name="data_subject_requests"
    ),  # noqa: F405
    # Kişisel veri envanteri
    path(
        "data-inventory/", personal_data_inventory, name="personal_data_inventory"
    ),  # noqa: F405
    # Güvenlik olayları
    path("incidents/", security_incidents, name="security_incidents"),  # noqa: F405
    # Veri yedekleme
    path("backup/", data_backup_management, name="data_backup"),  # noqa: F405
    # Şifreleme yönetimi
    path(
        "encryption/", encryption_management, name="encryption_management"
    ),  # noqa: F405
    # AJAX endpoints
    path(
        "ajax/compliance-check/", ajax_compliance_check, name="ajax_compliance_check"
    ),  # noqa: F405
    path(
        "ajax/security-metrics/", ajax_security_metrics, name="ajax_security_metrics"
    ),  # noqa: F405
]
