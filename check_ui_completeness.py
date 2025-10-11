"""UI completeness checker

Geliştirme: URL desenlerinden (Django) template adlarını keşfet ve
dosya sistemi taramasını yedek olarak kullan. Çıktı: eksik ekran adları.
"""

import os
from pathlib import Path

# 1) İstenen ekranlar (gerekirse yinelenenleri temizleyeceğiz)
required_screens = [
    "login", "register", "dashboard", "invoice_list", "invoice_create",
    "reporting", "ai_assistant", "education", "game", "audit", "settings", "blockchain",
    "advisor_profile", "taxpayer_profile", "engagement_list", "integrator_config", "access_token",
    "declaration_list", "declaration_detail", "submission_list", "submission_detail", "submission_log",
    "management_dashboard", "user_management", "role_management", "product_finans", "product_egitim",
    "product_blockchain", "product_oyunlar", "product_edonusum", "solution_entegrasyon", "solution_raporlama",
    "solution_analitik", "virtual_company_dashboard", "corporate", "corporate_about", "resources",
    "corporate_team", "support", "corporate_sustainability", "corporate_careers", "corporate_press",
    "corporate_investors", "corporate_security", "pricing", "blog", "legal", "kvkk", "contact", "search", "sitemap", "billing", "common", "health", "corporate_offer", 
    "resources_guides", "resources_docs", "resources_training", "support_live", "support_faq", "support_tech",
    "blog_news", "blog_expert", "blog_startup",
    "audit_log", "audit_report", "finance_overview", "finance_transactions", "finance_budgets", "finance_forecasting",
    "ai_chat", "ai_suggestions", "ai_history", "ai_settings",
    "game_list", "game_detail", "game_leaderboard", "game_profile",
    "blockchain_wallet", "blockchain_transactions", "blockchain_nfts", "blockchain_settings",
    "education_courses", "education_course_detail", "education_progress", "education_certificates",
    "tenancy_company", "tenancy_subscription", "tenancy_billing", "tenancy_users", "tenancy_settings",
    "billing_overview", "billing_invoices", "billing_payment_methods", "billing_subscriptions", "billing_history", "billing_settings",
    "user_profile", "user_security", "user_notifications", "user_preferences", "user_activity", "user_api_keys",
    "role_list", "role_detail", "role_permissions", "role_create", "role_edit", "role_delete",
    "engagement_detail", "engagement_create", "engagement_edit", "engagement_delete",
    "advisor_list", "advisor_detail", "advisor_create", "advisor_edit", "advisor_delete",
    "taxpayer_list", "taxpayer_detail", "taxpayer_create", "taxpayer_edit", "taxpayer_delete",
    "integrator_list", "integrator_detail", "integrator_create", "integrator_edit", "integrator_delete",
    "access_token_list", "access_token_detail", "access_token_create", "access_token_edit", "access_token_delete",
    "declaration_create", "declaration_edit", "declaration_delete",
    "submission_create", "submission_edit", "submission_delete", "submission_send", "submission_validate",
    "submissionlog_anchoring", "submissionlog_error", "submissionlog_info", "submissionlog_warning",
    "submissionlog_debug", "submissionlog_critical", "submissionlog_audit",
    "submissionlog_system", "submissionlog_user", "submissionlog_integration",
    "submissionlog_performance", "submissionlog_security", "submissionlog_compliance",
    "submissionlog_notification", "submissionlog_transaction", "submissionlog_data",
    "submissionlog_other", "submissionlog_all", "submissionlog_search", "submissionlog_filter",
    "submissionlog_export", "submissionlog_import", "submissionlog_archive", "submissionlog_restore",
    "submissionlog_truncate", "submissionlog_purge", "submissionlog_backup", "submissionlog_recovery",
    "submissionlog_monitoring", "submissionlog_reporting", "submissionlog_auditing", "submissionlog_alerting",
    "submissionlog_logging", "submissionlog_debugging", "submissionlog_analysis", "submissionlog_tracing",
    "submissionlog_profiling", "submissionlog_optimization", "submissionlog_tuning", "submissionlog_scaling",
    "submissionlog_maintenance", "submissionlog_operations", "submissionlog_development", "submissionlog_testing",
    "submissionlog_staging", "submissionlog_production", "submissionlog_environment", "submissionlog_configuration",
    "submissionlog_infrastructure", "submissionlog_platform", "submissionlog_service", "submissionlog_application",
    "submissionlog_component", "submissionlog_module", "submissionlog_function", "submissionlog_method",
    "submissionlog_class", "submissionlog_object", "submissionlog_instance", "submissionlog_attribute", "submissionlog_property",
    "submissionlog_event", "submissionlog_action", "submissionlog_task", "submissionlog_job", "submissionlog_process",
    "submissionlog_thread", "submissionlog_queue", "submissionlog_cache", "submissionlog_session", "submissionlog_cookie",
    "submissionlog_request", "submissionlog_response", "submissionlog_api", "submissionlog_endpoint", "submissionlog_route",
    "submissionlog_url", "submissionlog_path", "submissionlog_method", "submissionlog_header", "submissionlog_body",
    "submissionlog_parameter", "submissionlog_query", "submissionlog_form", "submissionlog_file", "submissionlog_upload",
    "submissionlog_download", "submissionlog_stream", "submissionlog_socket", "submissionlog_connection", "submissionlog_protocol",
    "submissionlog_security", "submissionlog_encryption", "submissionlog_authentication", "submissionlog_authorization", "submissionlog_audit", "submissionlog_compliance",
    "submissionlog_privacy", "submissionlog_data", "submissionlog_database", "submissionlog_table", "submissionlog_record", "submissionlog_field", "submissionlog_index",
    "submissionlog_query", "submissionlog_transaction", "submissionlog_backup", "submissionlog_restore", "submissionlog_replication", "submissionlog_sharding", "submissionlog_partitioning",
    "submissionlog_migration", "submissionlog_schema", "submissionlog_model", "submissionlog_entity", "submissionlog_attribute", "submissionlog_relationship", "submissionlog_constraint",
    "submissionlog_trigger", "submissionlog_procedure", "submissionlog_function", "submissionlog_view", "submissionlog_index", "submissionlog_sequence", "submissionlog_synonym",
    "submissionlog_user", "submissionlog_role", "submissionlog_permission", "submissionlog_group", "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event",
    "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric", "submissionlog_chart", "submissionlog_graph", "submissionlog_table",
    "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view", "submissionlog_export", "submissionlog_import",
    "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
    "submissionlog_export", "submissionlog_import", "submissionlog_search", "submissionlog_filter", "submissionlog_sort", "submissionlog_group", "submissionlog_ungroup", "submissionlog_select", "submissionlog_deselect", "submissionlog_bulk", "submissionlog_action",
    "submissionlog_workflow", "submissionlog_process", "submissionlog_task", "submissionlog_job", "submissionlog_event", "submissionlog_trigger", "submissionlog_condition", "submissionlog_rule",
    "submissionlog_policy", "submissionlog_audit", "submissionlog_log", "submissionlog_event", "submissionlog_alert", "submissionlog_notification", "submissionlog_report", "submissionlog_dashboard", "submissionlog_metric",
    "submissionlog_chart", "submissionlog_graph", "submissionlog_table", "submissionlog_list", "submissionlog_detail", "submissionlog_create", "submissionlog_edit", "submissionlog_delete", "submissionlog_view",
]


def _normalize_name(name: str) -> str:
    """Dosya yolundan veya template adından uzantısız, küçük harfli baz ad.
    Örn: 'products/finans.html' -> 'finans'
    """
    try:
        return Path(name).stem.lower()
    except Exception:
        name = str(name)
        return name.rsplit("/", 1)[-1].split(".")[0].lower()


def discover_templates_from_urls() -> set[str]:
    """Django URLConf üzerinden template adlarını keşfet.

    - CBV'lerde view.view_class.template_name denenir.
    - Mümkünse instance.get_template_names() çağrısı yapılır (hatalar yutulur).
    - FBV'lerde function.template_name attribute'u varsa alınır.

    Hata durumunda boş set döner.
    """
    templates: set[str] = set()
    try:
        import sys
        import django
        # manage.py ile aynı dizin yapısı için path eklemeye gerek olmamalı;
        # yine de güvenli olması için mevcut dosya konumundan tahmini yolları ekleyebiliriz.
        here = Path(__file__).resolve().parent
        repo_root = here
        # tests/ altında çalışıyor olabiliriz, kökü bulalım
        for _ in range(3):
            if (repo_root / "manage.py").exists():
                break
            repo_root = repo_root.parent
        inner = repo_root / "FinAsis"
        src = inner / "src"
        for p in (inner, src):
            if p.exists():
                sys.path.insert(0, str(p))

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.config.settings")
        django.setup()

        from django.urls import URLPattern, URLResolver, get_resolver

        def visit(pattern) -> None:
            from django.views.generic.base import TemplateView  # local import
            if isinstance(pattern, URLResolver):
                for p in pattern.url_patterns:
                    visit(p)
                return
            if isinstance(pattern, URLPattern):
                view = pattern.callback
                # CBV mi?
                view_class = getattr(view, "view_class", None)
                if view_class is not None:
                    # 1) Doğrudan attribute
                    tname = getattr(view_class, "template_name", None)
                    if tname:
                        templates.add(_normalize_name(tname))
                    # 2) Güvenli şekilde instance üzerinden get_template_names()
                    try:
                        inst = view_class()
                        # Bazı generic view'lar context'e ihtiyaç duyabilir; try/except
                        tnames = []
                        if getattr(inst, "template_name", None):
                            tnames = [inst.template_name]
                        else:
                            try:
                                tnames = list(inst.get_template_names())  # type: ignore[attr-defined]
                            except Exception:
                                tnames = []
                        for tn in tnames:
                            if tn:
                                templates.add(_normalize_name(tn))
                    except Exception:
                        pass
                    return

                # FBV: function attribute'u kontrol et
                tname = getattr(view, "template_name", None)
                if tname:
                    templates.add(_normalize_name(tname))
                return

        resolver = get_resolver()
        for p in resolver.url_patterns:
            visit(p)

    except Exception:
        # Django yoksa/ayarlar yüklenmiyorsa sessizce geç ve boş dön
        return set()

    return templates


def discover_templates_from_files() -> set[str]:
    exts = (".html", ".jsx", ".tsx", ".dart", ".kv")
    found: set[str] = set()
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(exts):
                found.add(_normalize_name(file))
    return found


def main() -> None:
    # Yinelenenleri temizle
    wanted = list(dict.fromkeys([s.strip().lower() for s in required_screens]))

    from_urls = discover_templates_from_urls()
    from_files = discover_templates_from_files()

    existing = sorted(from_urls.union(from_files))

    missing = [screen for screen in wanted if screen not in existing]

    if missing:
        print("❌ Eksik Ekranlar:")
        for m in missing:
            print("-", m)
    else:
        print("✅ Tüm UI ekranları mevcut görünüyor.")


if __name__ == "__main__":
    main()

