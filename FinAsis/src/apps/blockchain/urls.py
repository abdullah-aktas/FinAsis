from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/verify/', views.api_verify, name='api_verify'),
    path('api/verify-hash/', views.api_verify_hash, name='api_verify_hash'),
    path('api/anchor/', views.api_anchor, name='api_anchor'),
    path('records/', views.record_list, name='record_list'),
    path('records/create/', views.record_create, name='record_create'),
    path('records/export.csv', views.record_export_csv, name='record_export_csv'),
    # UI routes
    path('assets/', views.assets_list, name='assets_list'),
    path('transactions/', views.transactions_list, name='transactions_list'),
    path('contracts/', views.contracts_list, name='contracts_list'),
    path('reports/', views.reports, name='reports'),
    path('anchor/', views.anchor_wizard, name='anchor_wizard'),
    path('verify/', views.verify_wizard, name='verify_wizard'),
] 