from django.urls import path
from .views import forecast_financial_timeseries

urlpatterns = [
    path('forecast/', forecast_financial_timeseries, name='forecast_financial_timeseries'),
] 