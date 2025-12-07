# -*- coding: utf-8 -*-
"""
Core UI URLs
Temel UI Bileşenleri URL Yapılandırması
"""
from django.urls import path
from . import views

app_name = "core_ui"

urlpatterns = [
    # UI bileşenleri
    path("components/", views.ui_components, name="components"),
    path("theme/", views.theme_demo, name="theme_demo"),
    # AJAX endpoints
    path("ajax/theme-toggle/", views.ajax_theme_toggle, name="ajax_theme_toggle"),
    path(
        "ajax/user-preferences/",
        views.ajax_user_preferences,
        name="ajax_user_preferences",
    ),
]
