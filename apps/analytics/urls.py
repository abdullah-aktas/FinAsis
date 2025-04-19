from django.urls import path
from .views import dashboard, reports
from .views.dashboard import DashboardView

app_name = 'analytics'

urlpatterns = [
    # Pivot Tablo
    path('pivot/', dashboard.pivot_table_view, name='pivot_table'),
    path('pivot-data/', dashboard.get_pivot_data, name='pivot_data'),
    
    # İşlem Grid'i
    path('transactions/', reports.transaction_grid, name='transaction_grid'),
    path('transactions/list/', reports.get_transactions, name='get_transactions'),
    path('transactions/export/', reports.export_transactions, name='export_transactions'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
] 