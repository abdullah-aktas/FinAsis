from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard URLs
    path('dashboard/<int:dashboard_id>/', views.dashboard_view, name='dashboard'),
    
    # Widget URLs
    path('api/widget/<int:widget_id>/data/', views.get_widget_data, name='widget_data'),
    
    # Report URLs
    path('api/reports/create/', views.create_report, name='create_report'),
    path('api/reports/<int:report_id>/data/', views.get_report_data, name='report_data'),
    
    # Data Source URLs
    path('api/data-sources/add/', views.add_data_source, name='add_data_source'),
    path('api/data-sources/<int:source_id>/sync/', views.sync_data_source, name='sync_data_source'),
] 