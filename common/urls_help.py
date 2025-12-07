# -*- coding: utf-8 -*-
"""
Help System URLs
Yardım sistemi URL yapılandırması
"""

from django.urls import path
from . import views_help

app_name = "help"

urlpatterns = [
    # Ana yardım merkezi
    path("", views_help.help_center, name="center"),
    # Modül bazlı yardım
    path("module/<str:module_name>/", views_help.help_module, name="module"),
    # SSS
    path("faq/", views_help.help_faq, name="faq"),
    # Video eğitimler
    path("videos/", views_help.help_videos, name="videos"),
    # Klavye kısayolları
    path("shortcuts/", views_help.help_shortcuts, name="shortcuts"),
    # Hızlı başlangıç
    path("quick-start/", views_help.help_quick_start, name="quick_start"),
    # Destek talebi
    path("contact/", views_help.help_contact_support, name="contact"),
    # API endpoints
    path("api/search/", views_help.help_search, name="api_search"),
    path(
        "api/tooltip/<str:tooltip_key>/",
        views_help.help_api_tooltip,
        name="api_tooltip",
    ),
    path("api/tour/<str:tour_name>/", views_help.help_api_tour, name="api_tour"),
]
