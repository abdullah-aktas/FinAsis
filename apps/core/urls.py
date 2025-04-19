from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ... existing code ...
    
    # API Endpoints
    path('api/weather/', views.get_weather_data, name='weather_api'),
    path('api/finance/', views.get_finance_data, name='finance_api'),
] 