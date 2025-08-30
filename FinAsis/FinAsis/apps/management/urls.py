from django.urls import path, include
from .views import admin_dashboard, user_list, company_list, invoice_list, user_detail, user_add, user_edit, user_delete, invoice_detail, invoice_add, invoice_edit, invoice_delete, admin_logs, help_content_api, user_list_export_csv

urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    path('kullanicilar/', user_list, name='user_list'),
    path('kullanicilar/ekle/', user_add, name='user_add'),
    path('kullanicilar/<int:user_id>/', user_detail, name='user_detail'),
    path('kullanicilar/<int:user_id>/duzenle/', user_edit, name='user_edit'),
    path('kullanicilar/<int:user_id>/sil/', user_delete, name='user_delete'),
    path('kullanicilar/export/csv/', user_list_export_csv, name='user_list_export_csv'),
    path('sirketler/', company_list, name='company_list'),
    path('faturalar/', invoice_list, name='invoice_list'),
    path('faturalar/ekle/', invoice_add, name='invoice_add'),
    path('faturalar/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('faturalar/<int:invoice_id>/duzenle/', invoice_edit, name='invoice_edit'),
    path('faturalar/<int:invoice_id>/sil/', invoice_delete, name='invoice_delete'),
    path('superadmin/logs/', admin_logs, name='admin_logs'),
    path('api/', include('FinAsis.apps.management.api.urls')),
    path('api/help-content/', help_content_api, name='help_content_api'),
] 