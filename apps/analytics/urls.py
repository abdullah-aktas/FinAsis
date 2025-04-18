from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('charts/', views.charts, name='charts'),
    path('export/', views.export_data, name='export_data'),
] 