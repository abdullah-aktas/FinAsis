# -*- coding: utf-8 -*-
"""
Corporate URLs
Kurumsal İşletme Yönetimi URL Yapılandırması
"""
from django.urls import path
from . import views

app_name = "corporate"

urlpatterns = [
    # Ana sayfalar
    path("", views.corporate_landing, name="landing"),
    path("about/", views.about, name="about"),
    path("team/", views.team, name="team"),
    path("careers/", views.careers, name="careers"),
    path("investors/", views.investors, name="investors"),
    path("press/", views.press, name="press"),
    path("security/", views.security_page, name="security"),
    path("sustainability/", views.sustainability, name="sustainability"),
    path("dashboard/", views.corporate_dashboard, name="dashboard"),
    # Müşteri yönetimi
    path("clients/", views.client_list, name="client_list"),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/<int:client_id>/", views.client_detail, name="client_detail"),
    # Proje yönetimi
    path("projects/", views.project_list, name="project_list"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    # Sözleşme yönetimi
    path("contracts/", views.contract_list, name="contract_list"),
    # AJAX endpoints
    path("ajax/client-stats/", views.ajax_client_stats, name="ajax_client_stats"),
]
