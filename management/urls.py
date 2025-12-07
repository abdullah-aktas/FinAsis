from django.urls import path, include
from .views import (
    admin_dashboard,
    user_list,
    company_list,
    company_add,
    company_detail,
    company_edit,
    company_delete,
    invoice_list,
    user_detail,
    user_add,
    user_edit,
    user_delete,
    invoice_detail,
    invoice_add,
    invoice_edit,
    invoice_delete,
    admin_logs,
    help_content_api,
    user_list_export_csv,
    modules_list,
    module_detail,
)

urlpatterns = [
    path("", admin_dashboard, name="admin_dashboard"),
    # Modül Yönetimi
    path("modules/", modules_list, name="modules_list"),
    path("modules/<str:module_name>/", module_detail, name="module_detail"),
    # Kullanıcı Yönetimi
    path("kullanicilar/", user_list, name="user_list"),
    path("kullanicilar/ekle/", user_add, name="user_add"),
    path("kullanicilar/<int:user_id>/", user_detail, name="user_detail"),
    path("kullanicilar/<int:user_id>/duzenle/", user_edit, name="user_edit"),
    path("kullanicilar/<int:user_id>/sil/", user_delete, name="user_delete"),
    path("kullanicilar/export/csv/", user_list_export_csv, name="user_list_export_csv"),
    # Şirket Yönetimi
    path("sirketler/", company_list, name="company_list"),
    path("sirketler/ekle/", company_add, name="company_add"),
    path("sirketler/<int:company_id>/", company_detail, name="company_detail"),
    path("sirketler/<int:company_id>/duzenle/", company_edit, name="company_edit"),
    path("sirketler/<int:company_id>/sil/", company_delete, name="company_delete"),
    # Fatura Yönetimi
    path("faturalar/", invoice_list, name="invoice_list"),
    path("faturalar/ekle/", invoice_add, name="invoice_add"),
    path("faturalar/<int:invoice_id>/", invoice_detail, name="invoice_detail"),
    path("faturalar/<int:invoice_id>/duzenle/", invoice_edit, name="invoice_edit"),
    path("faturalar/<int:invoice_id>/sil/", invoice_delete, name="invoice_delete"),
    # Sistem
    path("superadmin/logs/", admin_logs, name="admin_logs"),
    path("api/", include("management.api.urls")),
    path("api/help-content/", help_content_api, name="help_content_api"),
]
