from django.urls import path
from .views import (
    forecast_financial_timeseries,
    JournalVoucherListCreateAPIView,
    JournalVoucherPostAPIView,
)

urlpatterns = [
    path('forecast/', forecast_financial_timeseries, name='forecast_financial_timeseries'),
    path('vouchers/', JournalVoucherListCreateAPIView.as_view(), name='journalvoucher_list_create'),
    path('vouchers/<int:pk>/post/', JournalVoucherPostAPIView.as_view(), name='journalvoucher_post'),
]