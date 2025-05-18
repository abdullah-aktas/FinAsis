# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('kobi-dashboard/', views.kobi_dashboard, name='kobi_dashboard'),
    path('export/', views.export_reports, name='export'),
] 