"""SEO utility definitions for sitemap generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class StaticPage:
    """Metadata for a static sitemap entry."""

    name: str
    kwargs: Mapping[str, Any] | None = None
    changefreq: str = "weekly"
    priority: float = 0.6


STATIC_PAGES: tuple[StaticPage, ...] = (
    StaticPage("home", changefreq="daily", priority=1.0),
    StaticPage("pricing", changefreq="weekly", priority=0.9),
    StaticPage("corporate:landing", changefreq="weekly", priority=0.8),
    StaticPage("corporate:team", changefreq="monthly", priority=0.5),
    StaticPage("support", changefreq="weekly", priority=0.7),
    StaticPage("resources", changefreq="weekly", priority=0.7),
    StaticPage("resources_guides", changefreq="weekly", priority=0.65),
    StaticPage("resources_docs", changefreq="weekly", priority=0.7),
    StaticPage("resources_training", changefreq="weekly", priority=0.6),
    StaticPage("resources_academy", changefreq="weekly", priority=0.6),
    StaticPage("resources_developer_hub", changefreq="weekly", priority=0.55),
    StaticPage("resources_partner_marketplace", changefreq="monthly", priority=0.5),
    StaticPage("products_muhasebe", changefreq="monthly", priority=0.65),
    StaticPage("products_finans", changefreq="monthly", priority=0.65),
    StaticPage("products_egitim", changefreq="monthly", priority=0.6),
    StaticPage("products_blockchain", changefreq="monthly", priority=0.6),
    StaticPage("products_oyunlar", changefreq="monthly", priority=0.55),
    StaticPage("products_edonusum", changefreq="monthly", priority=0.6),
    StaticPage("products_edenetim", changefreq="monthly", priority=0.6),
    StaticPage("products_yapay_zeka", changefreq="monthly", priority=0.6),
    StaticPage("solutions_enteg", changefreq="monthly", priority=0.6),
    StaticPage("solutions_raporlama", changefreq="monthly", priority=0.6),
    StaticPage("solutions_analitik", changefreq="monthly", priority=0.6),
    StaticPage("terms", changefreq="monthly", priority=0.6),
    StaticPage("privacy_policy", changefreq="monthly", priority=0.6),
    StaticPage("cookie_policy", changefreq="monthly", priority=0.5),
    StaticPage("legal", changefreq="monthly", priority=0.5),
    StaticPage("risk_warning", changefreq="monthly", priority=0.4),
    StaticPage("legal_kvkk", changefreq="monthly", priority=0.5),
    StaticPage("blog", changefreq="weekly", priority=0.5),
    StaticPage("resources_cfo_playbook", changefreq="monthly", priority=0.6),
    StaticPage("resources_compliance_checklist", changefreq="monthly", priority=0.6),
    StaticPage("training_finance_dashboard", changefreq="monthly", priority=0.5),
    StaticPage("training_compliance_engine", changefreq="monthly", priority=0.5),
    StaticPage("training_gamification_students", changefreq="monthly", priority=0.5),
    StaticPage("developer_api", changefreq="weekly", priority=0.7),
    StaticPage("accounting:company_list", changefreq="weekly", priority=0.6),
    StaticPage("accounting:report_redirect", changefreq="daily", priority=0.6),
    StaticPage("accounting:summary_report", changefreq="daily", priority=0.5),
    StaticPage("accounting:chart_data", changefreq="daily", priority=0.4),
    StaticPage("accounting:dashboard", changefreq="daily", priority=0.6),
    StaticPage("accounting:auto_book", changefreq="weekly", priority=0.4),
    StaticPage("accounting:rule_manager", changefreq="weekly", priority=0.4),
    StaticPage("accounting:financial_analysis", changefreq="weekly", priority=0.5),
    StaticPage("accounting:scenario_list", changefreq="weekly", priority=0.5),
)
