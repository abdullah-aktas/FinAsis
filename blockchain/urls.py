from django.urls import path
from . import views

app_name = "blockchain"

urlpatterns = [
    # Ana Dashboard
    path("", views.home, name="home"),
    # Block Yönetimi
    path("blocks/", views.block_list, name="block_list"),
    path("blocks/<int:block_number>/", views.block_detail, name="block_detail"),
    path("blocks/create/", views.create_new_block, name="create_block"),
    # Transaction Yönetimi
    path("transactions/", views.transaction_list, name="transaction_list"),
    path(
        "transactions/<str:transaction_id>/",
        views.transaction_detail,
        name="transaction_detail",
    ),
    path("transactions/create/", views.transaction_create, name="transaction_create"),
    # Smart Contract Yönetimi
    path("contracts/", views.contract_list, name="contract_list"),
    path(
        "contracts/<str:contract_address>/",
        views.contract_detail,
        name="contract_detail",
    ),
    path("contracts/deploy/", views.contract_deploy, name="contract_deploy"),
    path(
        "contracts/<str:contract_address>/execute/",
        views.contract_execute,
        name="contract_execute",
    ),
    # Digital Asset Yönetimi
    path("assets/", views.asset_list, name="asset_list"),
    path("assets/<str:asset_id>/", views.asset_detail, name="asset_detail"),
    path("assets/create/", views.asset_create, name="asset_create"),
    path("assets/my/", views.my_assets, name="my_assets"),
    # Legacy Routes (Geriye Uyumluluk)
    path("records/", views.record_list, name="record_list"),
    path("records/create/", views.record_create, name="record_create"),
    path("records/export.csv", views.record_export_csv, name="record_export_csv"),
    # API Endpoints
    path("api/verify/", views.api_verify, name="api_verify"),
    path("api/verify-hash/", views.api_verify_hash, name="api_verify_hash"),
    path("api/anchor/", views.api_anchor, name="api_anchor"),
    # Placeholder/Legacy UI Routes
    path("transactions-list/", views.transactions_list, name="transactions"),
    path("contracts-list/", views.contracts_list, name="contracts"),
    path("assets-list/", views.assets_list, name="assets"),
    path("reports/", views.reports, name="reports"),
    path("anchor/", views.anchor_wizard, name="anchor_wizard"),
    path("verify/", views.verify_wizard, name="verify_wizard"),
]
