# -*- coding: utf-8 -*-
"""
Core UI Views
Temel UI Bileşenleri ve Yardımcı Görünümler
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Dict, List

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.text import Truncator
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from accounts.models import Achievement
from accounting.models import Company
from accounting.models import Invoice as AccountingInvoice
from corporate.models import InvestorDocument, PressRelease
from common.context_processors import BRAND_IDENTITY
from ai_assistant.services import prompt_registry
from games import task_engine
from billing.models import Module as BillingModule
from billing.models import Plan

try:
    from partners.models import PartnerProfile, PartnerCategory
except Exception:  # pragma: no cover - partners app optional during migration
    PartnerProfile = None  # type: ignore[assignment]
    PartnerCategory = None  # type: ignore[assignment]


@dataclass(frozen=True)
class MarketingPageConfig:
    template_name: str
    title: str | None = None
    description: str | None = None


MARKETING_PAGES: dict[str, MarketingPageConfig] = {
    "pricing": MarketingPageConfig(
        template_name="pricing.html",
        title=_("FinAsis · Fiyatlandırma"),
        description=_("FinAsis fiyat planları ve abonelik seçenekleri."),
    ),
    "support": MarketingPageConfig(
        template_name="support.html",
        title=_("FinAsis · Destek Merkezi"),
        description=_(
            "FinAsis destek kanalları, yardım merkezi ve iletişim seçenekleri."
        ),
    ),
    "products_muhasebe": MarketingPageConfig(
        template_name="products/muhasebe.html",
        title=_("FinAsis · Akıllı Muhasebe Ekosistemi"),
    ),
    "products_finans": MarketingPageConfig(
        template_name="products/finans.html",
        title=_("FinAsis · Finansal Yönetim Platformu"),
    ),
    "products_egitim": MarketingPageConfig(
        template_name="products/egitim.html",
        title=_("FinAsis · Eğitim ve LMS Modülü"),
    ),
    "products_blockchain": MarketingPageConfig(
        template_name="products/blockchain.html",
        title=_("FinAsis · Blockchain Kanıt"),
    ),
    "products_oyunlar": MarketingPageConfig(
        template_name="products/oyunlar.html",
        title=_("FinAsis · Finansal Oyunlaştırma"),
    ),
    "products_edonusum": MarketingPageConfig(
        template_name="products/edonusum.html",
        title=_("FinAsis · e-Dönüşüm Çözümleri"),
    ),
    "products_edenetim": MarketingPageConfig(
        template_name="products/edenetim.html",
        title=_("FinAsis · e-Denetim Çözümleri"),
    ),
    "products_yapay_zeka": MarketingPageConfig(
        template_name="products/yapay_zeka.html",
        title=_("FinAsis · Yapay Zeka Asistanı"),
    ),
    "products_mali_musavir": MarketingPageConfig(
        template_name="products/mali_musavir.html",
        title=_("FinAsis · Mali Müşavirlik Platformu"),
    ),
    "products_kobi_analizi": MarketingPageConfig(
        template_name="products/kobi_analizi.html",
        title=_("FinAsis · KOBİ Analiz & Sağlık Platformu"),
    ),
    "solutions_enteg": MarketingPageConfig(
        template_name="solutions/entegrasyon.html",
        title=_("FinAsis · Sistem Entegrasyon Çözümleri"),
    ),
    "solutions_raporlama": MarketingPageConfig(
        template_name="solutions/raporlama.html",
        title=_("FinAsis · Gelişmiş Raporlama Çözümleri"),
    ),
    "solutions_analitik": MarketingPageConfig(
        template_name="solutions/analitik.html",
        title=_("FinAsis · Yapay Zeka Analitikleri"),
    ),
    "terms": MarketingPageConfig(
        template_name="terms.html",
        title=_("FinAsis · Kullanım Şartları"),
    ),
    "privacy_policy": MarketingPageConfig(
        template_name="privacy_policy.html",
        title=_("FinAsis · Gizlilik Politikası"),
    ),
    "cookie_policy": MarketingPageConfig(
        template_name="cookie_policy.html",
        title=_("FinAsis · Çerez Politikası"),
    ),
    "legal": MarketingPageConfig(
        template_name="legal.html",
        title=_("FinAsis · Hukuki Bilgiler"),
    ),
    "legal_kvkk": MarketingPageConfig(
        template_name="legal/kvkk.html",
        title=_("FinAsis · KVKK Aydınlatma Metni"),
    ),
    "risk_warning": MarketingPageConfig(
        template_name="risk_warning.html",
        title=_("FinAsis · Risk Bildirimi"),
    ),
    "blog": MarketingPageConfig(
        template_name="blog/index.html",
        title=_("FinAsis · Blog ve İçgörüler"),
        description=_(
            "Finans, uyumluluk ve dijital dönüşüm konularında FinAsis uzmanlarından makaleler."
        ),
    ),
    "resources_cfo_playbook": MarketingPageConfig(
        template_name="resources/cfo_playbook.html",
        title=_("FinAsis · SaaS CFO Oyun Kitabı"),
        description=_(
            "Finans liderleri için haftalık ritüeller, KPI tabloları ve raporlama şablonları."
        ),
    ),
    "resources_compliance_checklist": MarketingPageConfig(
        template_name="resources/compliance_checklist.html",
        title=_("FinAsis · Uyumluluk Checklist"),
        description=_(
            "MASAK ve KVKK uyumluluğu için operasyonel kontrol listeleri ve süreç rehberleri."
        ),
    ),
    "developer_api": MarketingPageConfig(
        template_name="resources/developer_api.html",
        title=_("FinAsis · Entegrasyon API Dokümantasyonu"),
        description=_(
            "REST API uç noktaları, kimlik doğrulama ve webhook entegrasyonu hakkında teknik rehber."
        ),
    ),
    "training_finance_dashboard": MarketingPageConfig(
        template_name="training/finance_dashboard.html",
        title=_("FinAsis · Finans Dashboard Eğitimi"),
        description=_(
            "KPI kartlarını yorumlama, nakit akışı senaryoları ve aksiyon planları."
        ),
    ),
    "training_compliance_engine": MarketingPageConfig(
        template_name="training/compliance_engine.html",
        title=_("FinAsis · Uyumluluk Motoru Eğitimi"),
        description=_(
            "MASAK kontrolleri, blockchain kayıtları ve denetim raporlaması."
        ),
    ),
    "training_gamification_students": MarketingPageConfig(
        template_name="training/gamification_students.html",
        title=_("FinAsis · Gamification ile Öğrenci Yönetimi"),
        description=_(
            "Oyunlaştırılmış LMS görevleri, puanlama motoru ve motivasyon akışı."
        ),
    ),
}


def _format_number(value: int | Decimal) -> str:
    return formats.number_format(value, force_grouping=True)


def _get_guide_catalogue() -> List[Dict[str, str]]:
    return [
        {
            "title": _("Finans Ekibi İçin İlk 30 Gün"),
            "summary": _(
                "Bankadan veri çekme, kategori kuralları ve KPI panosu oluşturma."
            ),
            "icon": "bi-graph-up-arrow",
            "category": _("Finans"),
            "read_time": _("10 dk"),
            "url": "/guides/finance-first-30-days/",
            "type": "guide",
        },
        {
            "title": _("Mali Müşavir Hızlı Kurulum"),
            "summary": _(
                "Müşteri onboarding, belge talepleri ve uyumluluk kontrolleri."
            ),
            "icon": "bi-briefcase",
            "category": _("Muhasebe"),
            "read_time": _("8 dk"),
            "url": "/guides/accountant-onboarding/",
            "type": "guide",
        },
        {
            "title": _("Öğretmenler İçin LMS Başlangıç"),
            "summary": _(
                "Ders planı oluşturma, quiz atama ve öğrenci ilerleme raporları."
            ),
            "icon": "bi-easel2",
            "category": _("Eğitim"),
            "read_time": _("6 dk"),
            "url": "/guides/teacher-lms-setup/",
            "type": "guide",
        },
        {
            "title": _("API Entegrasyon Temelleri"),
            "summary": _("OAuth2 yetkilendirme, test ortamı ve webhook dinleme."),
            "icon": "bi-braces",
            "category": _("Teknik"),
            "read_time": _("12 dk"),
            "url": reverse("developer_api"),
            "type": "guide",
        },
        {
            "title": _("Blockchain Audit Workflow"),
            "summary": _("Defter kayıtlarını zincire yazma ve doğrulama raporu alma."),
            "icon": "bi-link-45deg",
            "category": _("Blockchain"),
            "read_time": _("7 dk"),
            "url": "/guides/blockchain-audit/",
            "type": "guide",
        },
        {
            "title": _("Gamification ile Finans Öğretimi"),
            "summary": _("Oyun modülleri ile öğrenci başarısını artırma stratejileri."),
            "icon": "bi-controller",
            "category": _("Eğitim"),
            "read_time": _("9 dk"),
            "url": "/guides/gamification-learning/",
            "type": "guide",
        },
    ]


def _get_doc_categories() -> List[Dict[str, object]]:
    return [
        {
            "title": _("Kurulum"),
            "description": _(
                "SaaS ve kurum içi kurulum, ortam değişkenleri ve güvenlik yapılandırması."
            ),
            "icon": "bi-gear",
            "links": [
                {
                    "label": _("Kurulum Kontrol Listesi"),
                    "url": "/docs/setup/checklist/",
                },
                {"label": _("Ortam Değişkenleri"), "url": "/docs/setup/environment/"},
                {"label": _("Güvenlik Yapılandırma"), "url": "/docs/setup/security/"},
            ],
        },
        {
            "title": _("Muhasebe & Finans"),
            "description": _(
                "Muhasebe fişleri, e-belge entegrasyonları ve raporlama API'leri."
            ),
            "icon": "bi-calculator",
            "links": [
                {"label": _("e-Fatura Akışı"), "url": "/docs/accounting/e-invoice/"},
                {"label": _("Finansal KPI API"), "url": "/docs/finance/kpi-api/"},
                {
                    "label": _("Planlanan Raporlar"),
                    "url": "/docs/finance/scheduled-reports/",
                },
            ],
        },
        {
            "title": _("Geliştirici"),
            "description": _("REST API, webhook olayları, SDK'lar ve kimlik yönetimi."),
            "icon": "bi-code-slash",
            "links": [
                {"label": _("API Başlangıç"), "url": reverse("developer_api")},
                {"label": _("Webhook Rehberi"), "url": "/docs/developers/webhooks/"},
                {"label": _("OAuth2 Akışı"), "url": "/docs/developers/oauth/"},
            ],
        },
    ]


def _get_doc_library() -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for category in _get_doc_categories():
        for link in category["links"]:
            entries.append(
                {
                    "title": link["label"],
                    "description": category["description"],
                    "url": link["url"],
                    "category": category["title"],
                    "type": "docs",
                }
            )
    return entries


def _get_training_catalogue() -> List[Dict[str, str]]:
    return [
        {
            "title": _("Finans Dashboard'a Giriş"),
            "duration": _("18 dk"),
            "instructor": "Selin Kaya",
            "level": _("Başlangıç"),
            "publish_date": formats.date_format(date(2025, 7, 12), "DATE_FORMAT"),
            "url": reverse("training_finance_dashboard"),
            "type": "training",
            "description": _("KPI kartlarını okuma ve nakit akışı senaryoları."),
        },
        {
            "title": _("Uyumluluk Motoru İleri Seviye"),
            "duration": _("24 dk"),
            "instructor": "Murat Biçer",
            "level": _("Orta"),
            "publish_date": formats.date_format(date(2025, 6, 28), "DATE_FORMAT"),
            "url": reverse("training_compliance_engine"),
            "type": "training",
            "description": _("MASAK kontrolleri, blockchain audit ve raporlama."),
        },
        {
            "title": _("Gamification ile Öğrenci Yönetimi"),
            "duration": _("16 dk"),
            "instructor": "Ece Sarı",
            "level": _("Başlangıç"),
            "publish_date": formats.date_format(date(2025, 5, 30), "DATE_FORMAT"),
            "url": reverse("training_gamification_students"),
            "type": "training",
            "description": _("Oyunlaştırılmış LMS görevleri ve puanlama sistemi."),
        },
    ]


def landing_home(request):
    """
    FinAsis ana sayfası: finansal şirket yönetimi odağında modern pazarlama MVP'si.
    """
    primary_cta_config = BRAND_IDENTITY["cta"]["secondary"]
    secondary_cta_config = BRAND_IDENTITY["cta"]["primary"]

    user_model = get_user_model()
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    active_companies = Company.objects.filter(is_active=True)
    company_count = active_companies.count()

    active_user_count = user_model.objects.filter(is_active=True).count()

    monthly_invoices = AccountingInvoice.objects.filter(
        issue_date__gte=start_of_month,
        is_active=True,
    )
    invoice_aggregate = monthly_invoices.aggregate(
        total_amount=Sum("total_amount"),
        invoice_count=Count("id"),
    )
    monthly_invoice_total = invoice_aggregate["total_amount"] or Decimal("0")
    monthly_invoice_count = invoice_aggregate["invoice_count"] or 0

    module_qs = BillingModule.objects.filter(is_active=True).order_by("name")
    module_icon_map = {
        "finance_dashboard": "bi-speedometer2",
        "compliance": "bi-shield-check",
        "integration_hub": "bi-diagram-3",
        "education": "bi-mortarboard",
        "ai_assistant": "bi-robot",
        "games": "bi-controller",
    }
    modules = [
        {
            "name": module.name,
            "description": module.description,
            "icon": module_icon_map.get(module.code, "bi-layers"),
            "code": module.code,
        }
        for module in module_qs[:6]
    ]
    module_count = module_qs.count()

    plan_qs = (
        Plan.objects.filter(is_active=True)
        .prefetch_related("prices", "plan_modules__module")
        .order_by("audience", "name")
    )
    plans: List[Dict[str, object]] = []
    for plan in plan_qs[:4]:
        active_prices = [price for price in plan.prices.all() if price.is_active]
        active_price = active_prices[0] if active_prices else None
        plans.append(
            {
                "name": plan.name,
                "audience": (
                    plan.get_audience_display()
                    if hasattr(plan, "get_audience_display")
                    else plan.audience
                ),
                "description": plan.description,
                "price": active_price.amount if active_price else None,
                "price_period": (
                    active_price.get_period_display() if active_price else None
                ),
                "currency": active_price.currency if active_price else None,
                "code": plan.code,
            }
        )
    plan_count = plan_qs.count()

    achievements_qs = Achievement.objects.select_related("company").order_by(
        "-date_earned"
    )[:3]
    achievements = [
        {
            "title": achievement.title,
            "description": achievement.description,
            "company": achievement.company.name if achievement.company else "",
            "icon": achievement.icon,
            "date": formats.date_format(achievement.date_earned, "DATE_FORMAT"),
        }
        for achievement in achievements_qs
    ]

    press_releases = [
        {
            "title": press.title,
            "summary": press.summary,
            "date": formats.date_format(press.date, "DATE_FORMAT"),
            "url": press.url,
        }
        for press in PressRelease.objects.all()[:3]
    ]

    investor_documents = [
        {
            "title": doc.name,
            "kind": (
                doc.get_kind_display() if hasattr(doc, "get_kind_display") else doc.kind
            ),
            "url": doc.file_url,
            "published_at": (
                formats.date_format(doc.published_at, "DATE_FORMAT")
                if doc.published_at
                else ""
            ),
        }
        for doc in InvestorDocument.objects.all()[:3]
    ]

    ai_spotlight = (
        prompt_registry.get_prompts_for_role("kobi", limit=1)
        + prompt_registry.get_prompts_for_role("mali_musavir", limit=1)
        + prompt_registry.get_prompts_for_role("egitimci", limit=1)
    )

    prompt_catalog_size = sum(
        len(prompt_registry.get_prompts_for_role(role))
        for role in prompt_registry.list_roles()
    )

    teacher_brief = task_engine.get_brief(audience="teacher")
    student_brief = task_engine.get_brief(audience="student")
    gamer_brief = task_engine.get_brief(audience="gamer")

    mission_tiles = task_engine.get_tasks(audience="teacher", kind="mission", limit=1)
    mission_tiles += task_engine.get_tasks(
        audience="student", kind="challenge", limit=1
    )
    mission_tiles += task_engine.get_tasks(audience="gamer", kind="mission", limit=1)
    mission_tiles = mission_tiles[:3]

    partner_count = 0
    if PartnerProfile is not None:
        try:
            from django.db import connection
            from django.db.utils import OperationalError, ProgrammingError

            # Tablonun var olup olmadığını kontrol et
            table_name = PartnerProfile._meta.db_table
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        );
                    """,
                        [table_name],
                    )
                    table_exists = cursor.fetchone()[0]
                else:
                    # Diğer veritabanları için tablo kontrolü
                    table_exists = table_name in connection.introspection.table_names()

            if table_exists:
                partner_count = PartnerProfile.objects.filter(
                    status=PartnerProfile.Status.PUBLISHED
                ).count()
        except (OperationalError, ProgrammingError, Exception):
            # Üretim ortamında partners tabloları henüz oluşturulmadıysa
            partner_count = 0

    blockchain_tx_count = 0
    blockchain_contract_count = 0
    if apps.is_installed("blockchain"):
        try:
            from blockchain.models import Transaction as BlockchainTransaction
            from blockchain.models import SmartContract as BlockchainSmartContract

            blockchain_tx_count = BlockchainTransaction.objects.filter(
                status="confirmed"
            ).count()
            blockchain_contract_count = BlockchainSmartContract.objects.filter(
                is_active=True
            ).count()
        except Exception:
            blockchain_tx_count = 0
            blockchain_contract_count = 0

    metrics = [
        {
            "label": _("Aktif şirket"),
            "value": _format_number(company_count),
            "icon": "bi-buildings",
            "value_raw": company_count,
        },
        {
            "label": _("Aktif kullanıcı"),
            "value": _format_number(active_user_count),
            "icon": "bi-people",
            "value_raw": active_user_count,
        },
        {
            "label": _("Bu ay kesilen fatura"),
            "value": _format_number(monthly_invoice_count),
            "icon": "bi-file-earmark-bar-graph",
            "value_raw": monthly_invoice_count,
        },
        {
            "label": _("Bu ayki fatura hacmi"),
            "value": _("{amount} {currency}").format(
                amount=_format_number(monthly_invoice_total),
                currency=_("TRY"),
            ),
            "icon": "bi-cash-stack",
            "value_raw": monthly_invoice_total,
        },
        {
            "label": _("Aktif modül"),
            "value": _format_number(module_count),
            "icon": "bi-grid",
            "value_raw": module_count,
        },
        {
            "label": _("Canlı plan"),
            "value": _format_number(plan_count),
            "icon": "bi-kanban",
            "value_raw": plan_count,
        },
    ]

    has_metrics_activity = any(
        (isinstance(metric["value_raw"], Decimal) and metric["value_raw"] > 0)
        or (isinstance(metric["value_raw"], (int, float)) and metric["value_raw"] > 0)
        for metric in metrics
    )

    def _safe_reverse(name: str) -> str:
        try:
            return reverse(name)
        except Exception:
            return ""

    # Audit istatistikleri
    audit_event_count = 0
    audit_control_count = 0
    if apps.is_installed("audit"):
        try:
            from audit.models import AuditEvent, Control

            audit_event_count = AuditEvent.objects.count()
            audit_control_count = Control.objects.filter(is_active=True).count()
        except Exception:
            pass

    # Mali müşavir istatistikleri
    advisor_count = 0
    if apps.is_installed("advisors"):
        try:
            from advisors.models import AdvisorProfile

            advisor_count = AdvisorProfile.objects.filter(
                verified_at__isnull=False
            ).count()
        except Exception:
            pass

    # KOBİ Analizi istatistikleri
    kobi_analysis_count = 0
    if apps.is_installed("kobi_analysis"):
        try:
            from kobi_analysis.models import KOBIFinancialAnalysis

            kobi_analysis_count = KOBIFinancialAnalysis.objects.count()
        except Exception:
            pass

    solutions = [
        {
            "code": "accounting",
            "title": _("Muhasebe"),
            "icon": "bi-receipt",
            "color": "#0AAE94",
            "description": _(
                "Fatura, tahsilat ve banka entegrasyonlarını tek akışta yönetin; e-fatura ve e-arşiv çıktıları üretin."
            ),
            "href": _safe_reverse("products_muhasebe"),
            "stats": [
                {
                    "label": _("Toplam fatura"),
                    "value": _format_number(AccountingInvoice.objects.count()),
                },
                {"label": _("Aktif şirket"), "value": _format_number(company_count)},
            ],
        },
        {
            "code": "finance",
            "title": _("Finansal Yönetim"),
            "icon": "bi-graph-up-arrow",
            "color": "#10b981",
            "description": _(
                "KPI, bütçe, nakit akışı ve risk senaryoları ile finansal performansı gerçek zamanlı takip edin."
            ),
            "href": _safe_reverse("products_finans"),
            "stats": [
                {"label": _("Aktif şirket"), "value": _format_number(company_count)},
                {
                    "label": _("Toplam fatura"),
                    "value": _format_number(AccountingInvoice.objects.count()),
                },
            ],
        },
        {
            "code": "audit",
            "title": _("Denetim"),
            "icon": "bi-shield-check",
            "color": "#6366f1",
            "description": _(
                "İşlem kayıtları, risk değerlendirmeleri ve uyumluluk kontrolleri ile kapsamlı denetim yönetimi."
            ),
            "href": _safe_reverse("audit:landing"),
            "stats": [
                {
                    "label": _("Denetim kaydı"),
                    "value": _format_number(audit_event_count),
                },
                {
                    "label": _("Aktif kontrol"),
                    "value": _format_number(audit_control_count),
                },
            ],
        },
        {
            "code": "blockchain",
            "title": _("Blockchain"),
            "icon": "bi-link-45deg",
            "color": "#3b82f6",
            "description": _(
                "Blockchain kanıtı, akıllı sözleşmeler ve değiştirilemez kayıtlar ile işlemleri doğrulanabilir kılın."
            ),
            "href": _safe_reverse("products_blockchain"),
            "stats": [
                {
                    "label": _("Onaylanan işlem"),
                    "value": _format_number(blockchain_tx_count),
                },
                {
                    "label": _("Aktif sözleşme"),
                    "value": _format_number(blockchain_contract_count),
                },
            ],
        },
        {
            "code": "education",
            "title": _("Eğitim"),
            "icon": "bi-mortarboard",
            "color": "#f59e0b",
            "description": _(
                "Rol bazlı LMS, FinQuest görev motoru ve öğretmen panoları ile eğitim yönetimi."
            ),
            "href": _safe_reverse("products_egitim"),
            "stats": [
                {
                    "label": _("Öğretmen görevi"),
                    "value": _format_number(teacher_brief["task_count"]),
                },
                {
                    "label": _("Öğrenci görevi"),
                    "value": _format_number(student_brief["task_count"]),
                },
            ],
        },
        {
            "code": "games",
            "title": _("Oyunlar"),
            "icon": "bi-controller",
            "color": "#8b5cf6",
            "description": _(
                "Finansal okuryazarlığı ligler, görevler ve simülasyonlarla güçlendiren oyunlaştırma platformu."
            ),
            "href": _safe_reverse("products_oyunlar"),
            "stats": [
                {"label": _("Aktif oyuncu"), "value": _format_number(0)},
                {"label": _("Tamamlanan görev"), "value": _format_number(0)},
            ],
        },
        {
            "code": "advisors",
            "title": _("Mali Müşavirlik"),
            "icon": "bi-briefcase",
            "color": "#2563eb",
            "description": _(
                "Mali müşavir marketplace, müşteri yönetimi, danışmanlık oturumları ve raporlama sistemi."
            ),
            "href": _safe_reverse("products_mali_musavir"),
            "stats": [
                {"label": _("Onaylı müşavir"), "value": _format_number(advisor_count)},
                {
                    "label": _("Yayınlanan partner"),
                    "value": _format_number(partner_count),
                },
            ],
        },
        {
            "code": "ai-assistant",
            "title": _("Yapay Zeka"),
            "icon": "bi-robot",
            "color": "#8b5cf6",
            "description": _(
                "Rol bazlı Türkçe prompt kütüphanesi ve doğal dil rapor üretimiyle finans ekiplerini hızlandırın."
            ),
            "href": _safe_reverse("products_yapay_zeka"),
            "stats": [
                {
                    "label": _("Yayınlanan prompt"),
                    "value": _format_number(prompt_catalog_size),
                },
                {
                    "label": _("Öne çıkan AI kartı"),
                    "value": _format_number(len(ai_spotlight)),
                },
            ],
        },
        {
            "code": "kobi-analysis",
            "title": _("KOBİ Analizi"),
            "icon": "bi-graph-up",
            "color": "#dc2626",
            "description": _(
                "AI destekli finansal analiz, KOBİ sağlık skoru, risk yönetimi ve büyüme önerileri."
            ),
            "href": _safe_reverse("products_kobi_analizi"),
            "stats": [
                {"label": _("Aktif şirket"), "value": _format_number(company_count)},
                {
                    "label": _("Yapılan analiz"),
                    "value": _format_number(kobi_analysis_count),
                },
            ],
        },
        {
            "code": "e-donusum",
            "title": _("e-Dönüşüm"),
            "icon": "bi-file-earmark-check",
            "color": "#f59e0b",
            "description": _(
                "e-Fatura, e-Arşiv, e-Defter. GİB onaylı entegrasyon, kağıtsız süreçler ve maliyet azaltımı."
            ),
            "href": _safe_reverse("products_edonusum"),
            "stats": [
                {
                    "label": _("Toplam fatura"),
                    "value": _format_number(AccountingInvoice.objects.count()),
                },
                {"label": _("Aktif şirket"), "value": _format_number(company_count)},
            ],
        },
    ]

    if not modules:
        modules = [
            {
                "name": solution["title"],
                "description": solution["description"],
                "icon": solution["icon"],
                "code": solution["code"],
            }
            for solution in solutions[:4]
        ]

    customer_segments: List[Dict[str, object]] = []
    for plan in plan_qs:
        active_prices = [price for price in plan.prices.all() if price.is_active]
        monthly_price = next(
            (price for price in active_prices if price.period == "month"), None
        )
        yearly_price = next(
            (price for price in active_prices if price.period == "year"), None
        )
        plan_modules_manager = getattr(plan, "plan_modules", None)
        if plan_modules_manager is not None:
            sample_modules = [
                pm.module.name
                for pm in plan_modules_manager.all()[:3]
                if getattr(pm, "module", None) and pm.module.is_active
            ]
        else:
            sample_modules = []
        customer_segments.append(
            {
                "code": plan.code,
                "name": plan.name,
                "audience": (
                    plan.get_audience_display()
                    if hasattr(plan, "get_audience_display")
                    else plan.audience
                ),
                "description": plan.description,
                "monthly_price": monthly_price.amount if monthly_price else None,
                "yearly_price": yearly_price.amount if yearly_price else None,
                "currency": (
                    (monthly_price or yearly_price).currency
                    if (monthly_price or yearly_price)
                    else None
                ),
                "modules": sample_modules,
            }
        )

    hero_stats = metrics[:3]

    resource_cards: List[Dict[str, object]] = []
    if press_releases:
        resource_cards.append(
            {
                "title": _("Basın & Duyurular"),
                "items": [
                    {
                        "label": press["title"],
                        "meta": press["date"],
                        "href": press["url"] or _safe_reverse("corporate:landing"),
                    }
                    for press in press_releases
                ],
                "cta": {
                    "label": _("Tüm kurumsal haberler"),
                    "href": _safe_reverse("corporate:landing"),
                },
            }
        )
    if investor_documents:
        resource_cards.append(
            {
                "title": _("Yatırımcı Dokümanları"),
                "items": [
                    {
                        "label": doc["title"],
                        "meta": doc["published_at"],
                        "href": doc["url"],
                    }
                    for doc in investor_documents
                ],
                "cta": {
                    "label": _("Yatırımcı merkezi"),
                    "href": _safe_reverse("corporate:landing"),
                },
            }
        )
    ai_assistant_library_url = _safe_reverse("ai_assistant:guide") or _safe_reverse(
        "ai_assistant:dashboard"
    )
    if ai_spotlight and ai_assistant_library_url:
        resource_cards.append(
            {
                "title": _("AI Asistan Kartları"),
                "items": [
                    {
                        "label": prompt["title"],
                        "meta": prompt.get("cta_label"),
                        "href": prompt.get("cta_href"),
                    }
                    for prompt in ai_spotlight
                ],
                "cta": {
                    "label": _("AI asistan kitaplığı"),
                    "href": ai_assistant_library_url,
                },
            }
        )

    gamer_journey_url = _safe_reverse("games:quests_home") or _safe_reverse(
        "games:index"
    )

    journeys = [
        {
            "title": _("Öğretmen akışı"),
            "audience": _("Öğretmen"),
            "task_count": teacher_brief["task_count"],
            "total_xp": teacher_brief["total_reward_xp"],
            "tags": teacher_brief["tags"][:3],
            "href": _safe_reverse("resources_academy"),
        },
        {
            "title": _("Öğrenci başarısı"),
            "audience": _("Öğrenci"),
            "task_count": student_brief["task_count"],
            "total_xp": student_brief["total_reward_xp"],
            "tags": student_brief["tags"][:3],
            "href": _safe_reverse("resources_training"),
        },
        {
            "title": _("Oyunlaştırma programı"),
            "audience": _("Gamifier"),
            "task_count": gamer_brief["task_count"],
            "total_xp": gamer_brief["total_reward_xp"],
            "tags": gamer_brief["tags"][:3],
            "href": gamer_journey_url,
        },
    ]

    # primary_navigation kaldırıldı - header varsayılan linkleri kullanacak
    # Artık header.html'deki varsayılan navigasyon kullanılacak
    primary_navigation = None

    secondary_navigation = []

    hero_description = _(
        "KOBİ sahipleri, muhasebeciler, mali müşavirler, öğretmenler, öğrenciler ve finansı oyunlaştırarak öğrenmek isteyenler için "
        "yerel AI destekli tek platform; beta kampanyasında her kayıt 1 hisse + 2 ay ücretsiz erişim ve blockchain yatırımcı sözleşmesi kazanır."
    )

    hero = {
        "eyebrow": _("Yerel AI finans platformu"),
        "title": _("Finans, uyum ve eğitim ekipleri için tek ekosistem."),
        "description": hero_description,
        "primary_cta": {
            "label": _(primary_cta_config["label"]),
            "href": reverse(primary_cta_config["url_name"]),
            "cta_id": f"hero-{primary_cta_config['url_name'].replace(':', '-')}",
            "icon": primary_cta_config.get("icon", "calendar-event"),
        },
        "secondary_cta": {
            "label": _(secondary_cta_config["label"]),
            "href": reverse(secondary_cta_config["url_name"]),
            "cta_id": f"hero-{secondary_cta_config['url_name'].replace(':', '-')}",
            "icon": secondary_cta_config.get("icon", "rocket-takeoff"),
        },
        "month_range": {
            "start": formats.date_format(start_of_month, "DATE_FORMAT"),
            "end": formats.date_format(today, "DATE_FORMAT"),
        },
    }

    ecosystem = {
        "partner_count": partner_count,
        "press_release_count": PressRelease.objects.count(),
        "document_count": InvestorDocument.objects.count(),
    }

    audience_tiles = [
        {
            "icon": "bi-briefcase",
            "title": _("KOBİ Sahipleri"),
            "summary": _(
                "Nakit akışı, banka entegrasyonu ve gerçek zamanlı raporlarla şirket finansını tek ekrandan yönetin."
            ),
        },
        {
            "icon": "bi-calculator",
            "title": _("Muhasebeciler & Mali Müşavirler"),
            "summary": _(
                "Marketplace üzerinden müşteri yönetin, e-Fatura ve beyannameleri AI destekli kontrol edin."
            ),
        },
        {
            "icon": "bi-mortarboard",
            "title": _("Öğretmenler"),
            "summary": _(
                "FinQuest görev motoru ile muhasebe-finans derslerini oyunlaştırarak aktarın."
            ),
        },
        {
            "icon": "bi-person-workspace",
            "title": _("Öğrenciler"),
            "summary": _(
                "Canlı görevler, quizler ve rapor simülasyonlarıyla uygulamalı öğrenme."
            ),
        },
        {
            "icon": "bi-graph-up-arrow",
            "title": _("Finans Profesyonelleri"),
            "summary": _(
                "Portföy, uyum ve blockchain denetim izlerini tek yerden izleyerek kariyerinizi güçlendirin."
            ),
        },
        {
            "icon": "bi-controller",
            "title": _("Oyunlaştırma Tutkunları"),
            "summary": _(
                "Finans temalı oyunlar ve turnuvalarla veri okuryazarlığını eğlenceli şekilde geliştirin."
            ),
        },
    ]

    context = {
        "page_title": _("FinAsis · Finansal Şirket Yönetimi Platformu"),
        "hero": hero,
        "metrics": metrics,
        "has_metrics_activity": has_metrics_activity,
        "hero_stats": hero_stats,
        "modules": modules,
        "plans": plans,
        "achievements": achievements,
        "press_releases": press_releases,
        "investor_documents": investor_documents,
        "ai_spotlight": ai_spotlight,
        "missions": mission_tiles,
        "ecosystem": ecosystem,
        "solutions": solutions,
        "customer_segments": customer_segments,
        "resource_cards": resource_cards,
        "journeys": journeys,
        "audience_tiles": audience_tiles,
        "primary_navigation": primary_navigation,  # None - header varsayılan linkleri kullanacak
        "secondary_navigation": secondary_navigation,
        "teacher_brief": teacher_brief,
        "student_brief": student_brief,
        "gamer_brief": gamer_brief,
    }
    return render(request, "pages/home.html", context)


def resource_hub(request):
    """
    Resource hub landing page that consolidates guides, documentation, training and support.
    """
    guides = _get_guide_catalogue()
    doc_entries = _get_doc_library()
    trainings = _get_training_catalogue()

    resource_tiles = [
        {
            "title": _("Kılavuzlar"),
            "description": _(
                "Modüller ve persona senaryoları için adım adım rehberler."
            ),
            "href": reverse("resources_guides"),
            "icon": "bi-journal-text",
            "accent": "#10b981",
            "cta_label": _("Kılavuzlar"),
        },
        {
            "title": _("Dokümantasyon"),
            "description": _(
                "API referansları, entegrasyon yönergeleri ve kurulum dökümanları."
            ),
            "href": reverse("resources_docs"),
            "icon": "bi-file-earmark-code",
            "accent": "#3b82f6",
            "cta_label": _("Dokümantasyon"),
        },
        {
            "title": _("Eğitim"),
            "description": _(
                "Video dersler, canlı eğitim programları ve oyunlaştırılmış öğrenme modülleri."
            ),
            "href": reverse("resources_training"),
            "icon": "bi-mortarboard",
            "accent": "#f59e0b",
            "cta_label": _("Eğitimler"),
        },
        {
            "title": _("FinAsis Academy"),
            "description": _(
                "Öğretmen ve öğrenciler için rol bazlı ders scriptleri, görev motoru ve sertifika içerikleri."
            ),
            "href": reverse("resources_academy"),
            "icon": "bi-mortarboard-fill",
            "accent": "#0ea5e9",
            "cta_label": _("Academy"),
        },
        {
            "title": _("Developer Hub"),
            "description": _(
                "API örnekleri, webhook test konsolu ve topluluk etkinlikleri."
            ),
            "href": reverse("resources_developer_hub"),
            "icon": "bi-code-slash",
            "accent": "#6366f1",
            "cta_label": _("Developer"),
        },
        {
            "title": _("Partner Marketplace"),
            "description": _(
                "Entegratör ve çözüm ortaklarını keşfedin, pazar yerinden modül ekleyin."
            ),
            "href": reverse("resources_partner_marketplace"),
            "icon": "bi-shop-window",
            "accent": "#f43f5e",
            "cta_label": _("Marketplace"),
        },
    ]

    featured_resources = [
        {
            "title": _("SaaS CFO Oyun Kitabı"),
            "description": _(
                "Büyüyen şirketler için haftalık finans ritüelleri ve KPI tabloları."
            ),
            "href": reverse("resources_cfo_playbook"),
            "icon": "bi-diagram-3",
            "accent": "#7c3aed",
            "category": _("Finans"),
            "type": "guide",
        },
        {
            "title": _("Uyumluluk Checklist"),
            "description": _(
                "MASAK ve KVKK uyumluluğu için operasyonel checklist şablonları."
            ),
            "href": reverse("resources_compliance_checklist"),
            "icon": "bi-shield-check",
            "accent": "#0aae94",
            "category": _("Uyumluluk"),
            "type": "guide",
        },
        {
            "title": _("FinAsis Entegrasyon API"),
            "description": _(
                "REST & webhook uç noktaları, kimlik doğrulama ve örnek istekler."
            ),
            "href": reverse("developer_api"),
            "icon": "bi-braces",
            "accent": "#2563eb",
            "category": _("Teknik"),
            "type": "docs",
        },
    ]

    support_topics = [
        {
            "title": _("Destek Merkezi"),
            "description": _("SSS, sorun giderme ve kullanıcı topluluğu."),
            "href": reverse("support"),
            "icon": "bi-question-diamond",
            "accent": "#ec4899",
            "badges": [_("SSS"), _("Topluluk"), _("İletişim")],
        },
        {
            "title": _("Canlı Destek"),
            "description": _("Hafta içi 09:00-21:00 arasında canlı sohbet ve telefon."),
            "href": "/support/live/",
            "icon": "bi-chat-dots",
            "accent": "#10b981",
            "badges": [_("Sohbet"), _("Telefon")],
        },
        {
            "title": _("Teknik Durum"),
            "description": _("Sistem durumu, bakım takvimi ve SLA bildirimleri."),
            "href": "/support/status/",
            "icon": "bi-activity",
            "accent": "#f97316",
            "badges": [_("SLA"), _("Bakım"), _("Bildirim")],
            "category": _("Destek"),
            "type": "support",
        },
        {
            "title": _("Entegrasyon Destek"),
            "description": _("API anahtarı yönetimi, webhook ve sandbox erişimi."),
            "href": "/support/tech/",
            "icon": "bi-plug",
            "accent": "#6366f1",
            "badges": [_("API"), _("Sandbox")],
            "category": _("Teknik"),
            "type": "support",
        },
    ]

    popular_searches = ["e-Fatura", "API", "Uyumluluk", "Finans Dashboard", "SLA"]

    ecosystem_entries = [
        {
            "title": _("FinAsis Academy"),
            "description": _(
                "Rol bazlı ders scriptleri, görev motoru ve sertifika programları."
            ),
            "url": reverse("resources_academy"),
            "category": _("Topluluk"),
            "type": "academy",
        },
        {
            "title": _("Developer Community"),
            "description": _(
                "API örnek kodları, webhook test konsolu ve topluluk etkinlikleri."
            ),
            "url": reverse("resources_developer_hub"),
            "category": _("Teknik"),
            "type": "community",
        },
        {
            "title": _("Partner Marketplace"),
            "description": _(
                "Entegrasyon partnerleri, ERP/CRM çözümleri ve ortak kampanyalar."
            ),
            "url": reverse("resources_partner_marketplace"),
            "category": _("Ekosistem"),
            "type": "marketplace",
        },
    ]

    library: List[Dict[str, str]] = []
    for item in guides:
        library.append(
            {
                "title": item["title"],
                "description": item["summary"],
                "url": item["url"],
                "category": item["category"],
                "type": "guide",
            }
        )
    for item in doc_entries:
        library.append(
            {
                "title": item["title"],
                "description": item["description"],
                "url": item["url"],
                "category": item["category"],
                "type": "docs",
            }
        )
    for item in trainings:
        library.append(
            {
                "title": item["title"],
                "description": item["description"],
                "url": item["url"],
                "category": _("Eğitim"),
                "type": "training",
            }
        )
    for item in featured_resources:
        library.append(
            {
                "title": item["title"],
                "description": item["description"],
                "url": item["href"],
                "category": item.get("category", _("Öne Çıkanlar")),
                "type": item.get("type", "guide"),
            }
        )
    for item in support_topics:
        library.append(
            {
                "title": item["title"],
                "description": item["description"],
                "url": item["href"],
                "category": item.get("category", _("Destek")),
                "type": item.get("type", "support"),
            }
        )
    for item in ecosystem_entries:
        library.append(item)

    search_query = request.GET.get("q", "").strip()
    search_category = request.GET.get("category", "").strip()
    search_results = library

    if search_category:
        search_results = [
            entry
            for entry in search_results
            if entry["category"].lower() == search_category.lower()
        ]
    if search_query:
        lowered = search_query.lower()
        search_results = [
            entry
            for entry in search_results
            if lowered in entry["title"].lower()
            or lowered in entry["description"].lower()
        ]

    categories = sorted({entry["category"] for entry in library})
    types = sorted({entry["type"] for entry in library})

    context = {
        "page_title": _("FinAsis · Resource Hub"),
        "resource_tiles": resource_tiles,
        "featured_resources": featured_resources,
        "support_topics": support_topics,
        "popular_searches": popular_searches,
        "search_query": search_query,
        "search_category": search_category,
        "search_results": search_results[:12],
        "resource_categories": categories,
        "resource_types": types,
        "total_results": len(search_results),
    }
    return render(request, "resources.html", context)


def resource_guides(request):
    """
    Persona and module oriented getting started guides.
    """
    guides = _get_guide_catalogue()
    context = {
        "page_title": _("FinAsis · Kılavuzlar"),
        "guides": guides,
    }
    return render(request, "resources/guides.html", context)


def resource_docs(request):
    """
    Documentation landing with categories and latest updates.
    """
    categories = _get_doc_categories()

    latest_updates = [
        {
            "date": formats.date_format(date(2025, 10, 2), "DATE_FORMAT"),
            "title": _("Webhook İmzalama"),
            "summary": _(
                "Tüm webhook payload'ları için HMAC-SHA256 imzalama zorunlu hale getirildi."
            ),
            "url": "/docs/developers/webhooks/signing/",
        },
        {
            "date": formats.date_format(date(2025, 9, 18), "DATE_FORMAT"),
            "title": _("Yeni Finans KPI Uç Noktası"),
            "summary": _(
                "`/api/v2/finance/kpi` uç noktası günlük KPI özetlerini döndürüyor."
            ),
            "url": "/docs/finance/kpi-api/#v2",
        },
        {
            "date": formats.date_format(date(2025, 8, 30), "DATE_FORMAT"),
            "title": _("Özel Roller API"),
            "summary": _(
                "RBAC politikaları için yeni roller ve izin şemaları yayınlandı."
            ),
            "url": "/docs/security/rbac/",
        },
    ]

    context = {
        "page_title": _("FinAsis · Dokümantasyon"),
        "categories": categories,
        "latest_updates": latest_updates,
    }
    return render(request, "resources/docs.html", context)


def resource_training(request):
    """
    Training catalogue page with video lessons metadata.
    """
    video_lessons = _get_training_catalogue()
    context = {
        "page_title": _("FinAsis · Eğitim Kaynakları"),
        "video_lessons": video_lessons,
    }
    return render(request, "resources/training.html", context)


def resource_academy(request):
    teacher_prompts = prompt_registry.get_prompts_for_role("egitimci", limit=3)
    student_prompts = prompt_registry.get_prompts_for_role("ogrenci", limit=3)
    teacher_tasks = task_engine.get_tasks(audience="teacher", kind="mission", limit=3)
    student_tasks = task_engine.get_tasks(audience="student", kind="mission", limit=3)
    context = {
        "page_title": _("FinAsis · Academy"),
        "teacher_prompts": teacher_prompts,
        "student_prompts": student_prompts,
        "teacher_tasks": teacher_tasks,
        "student_tasks": student_tasks,
    }
    return render(request, "resources/academy.html", context)


def resource_developer_hub(request):
    api_resources = [
        {"label": _("REST API Başlangıç"), "url": reverse("developer_api")},
        {"label": _("Webhook Test Konsolu"), "url": "/developers/webhooks/"},
        {"label": _("SDK & Örnek Kodlar"), "url": "/developers/sdk/"},
    ]
    community_updates = [
        {
            "title": _("FinAsis Developer Connect"),
            "date": formats.date_format(date(2025, 11, 30), "DATE_FORMAT"),
            "format": _("Çevrim içi webinar"),
        },
        {
            "title": _("Hackathon: Finansal Simülasyonlar"),
            "date": formats.date_format(date(2026, 1, 18), "DATE_FORMAT"),
            "format": _("Hibrit"),
        },
    ]
    metrics = task_engine.get_brief(audience="gamer")
    context = {
        "page_title": _("FinAsis · Developer Hub"),
        "api_resources": api_resources,
        "community_updates": community_updates,
        "metrics": metrics,
    }
    return render(request, "resources/developer_hub.html", context)


def resource_partner_marketplace(request):
    partner_listings: list[dict[str, str]] = []
    partner_categories: list[dict[str, str]] = []

    if PartnerProfile is not None:
        try:
            from django.db import connection
            from django.db.utils import OperationalError, ProgrammingError

            # Tablonun var olup olmadığını kontrol et
            table_name = PartnerProfile._meta.db_table
            with connection.cursor() as cursor:
                if connection.vendor == "postgresql":
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        );
                    """,
                        [table_name],
                    )
                    table_exists = cursor.fetchone()[0]
                else:
                    table_exists = table_name in connection.introspection.table_names()

            if not table_exists:
                partner_listings = []
                partner_categories = []
            else:
                qs = (
                    PartnerProfile.objects.filter(
                        status=PartnerProfile.Status.PUBLISHED
                    )
                    .select_related("category")
                    .order_by("-is_featured", "sort_order", "name")
                )
                for partner in qs:
                    partner_listings.append(
                        {
                            "name": partner.name,
                            "headline": partner.headline or partner.integration_focus,
                            "category": (
                                partner.category.name if partner.category_id else ""
                            ),
                            "description": partner.description,
                            "badge": partner.badge_label
                            or (_("Öne Çıkan Partner") if partner.is_featured else ""),
                            "website": partner.website_url,
                        }
                    )

                if PartnerCategory is not None:
                    cat_qs = PartnerCategory.objects.order_by("sort_order", "name")
                    partner_categories = [
                        {
                            "name": cat.name,
                            "description": cat.description,
                            "icon": cat.icon,
                            "code": cat.code,
                        }
                        for cat in cat_qs
                    ]
        except (OperationalError, ProgrammingError, Exception):
            partner_listings = []
            partner_categories = []

    if not partner_listings:
        partner_listings = [
            {
                "name": "LedgerOne ERP",
                "headline": _("Finans ve stok entegrasyonu"),
                "category": _("ERP Entegrasyonu"),
                "description": _(
                    "Gelir ve stok verilerini FinAsis'e gerçek zamanlı aktarır."
                ),
                "badge": _("Premium Partner"),
                "website": "",
            },
            {
                "name": "TaxPro EU",
                "headline": _("AB VAT otomatizasyonu"),
                "category": _("Vergi Uyum"),
                "description": _(
                    "EU VAT, OSS ve dijital beyan süreçleri için hazır entegrasyon."
                ),
                "badge": _("Yeni"),
                "website": "",
            },
            {
                "name": "Compliance360",
                "headline": _("Risk skorlama danışmanlığı"),
                "category": _("Uyumluluk Danışmanlığı"),
                "description": _("AML, KYT ve risk skorlama için uzman danışmanlık."),
                "badge": _("Global"),
                "website": "",
            },
        ]
    onboarding_steps = [
        {
            "step": 1,
            "title": _("Başvuru ve değerlendirme"),
            "detail": _("Partner portalı üzerinden başvuru ve güvenlik taraması."),
        },
        {
            "step": 2,
            "title": _("Sandbox doğrulaması"),
            "detail": _("API entegrasyonu ve görev motoru senaryolarının testi."),
        },
        {
            "step": 3,
            "title": _("Marketplace yayını"),
            "detail": _("Fiyatlandırma, SLA ve destek bilgileriyle yayın."),
        },
    ]
    context = {
        "page_title": _("FinAsis · Partner Marketplace"),
        "partner_listings": partner_listings,
        "onboarding_steps": onboarding_steps,
        "partner_categories": partner_categories,
        "partner_count": len(partner_listings),
    }
    return render(request, "resources/partner_marketplace.html", context)


def _get_product_stats(page_key: str) -> Dict[str, object]:
    """Her ürün sayfası için dinamik istatistikleri hesapla"""
    stats = {}

    if page_key == "products_muhasebe":
        # Muhasebe istatistikleri
        stats["total_invoices"] = AccountingInvoice.objects.count()
        stats["company_count"] = Company.objects.filter(is_active=True).count()
        today = timezone.localdate()
        start_of_month = today.replace(day=1)
        monthly_invoices = AccountingInvoice.objects.filter(
            issue_date__gte=start_of_month,
            is_active=True,
        )
        stats["monthly_invoices"] = monthly_invoices.count()
        monthly_total = monthly_invoices.aggregate(total=Sum("total_amount"))[
            "total"
        ] or Decimal("0")
        stats["monthly_total"] = monthly_total

    elif page_key == "products_finans":
        # Finansal Yönetim istatistikleri
        stats["company_count"] = Company.objects.filter(is_active=True).count()
        stats["total_invoices"] = AccountingInvoice.objects.count()
        if apps.is_installed("finance"):
            try:
                from finance.models import Transaction as FinanceTransaction

                stats["total_transactions"] = FinanceTransaction.objects.count()
                today = timezone.localdate()
                start_of_month = today.replace(day=1)
                monthly_transactions = FinanceTransaction.objects.filter(
                    date__gte=start_of_month,
                )
                stats["monthly_transactions"] = monthly_transactions.count()
            except Exception:
                stats["total_transactions"] = 0
                stats["monthly_transactions"] = 0

    elif page_key == "products_blockchain":
        # Blockchain istatistikleri
        if apps.is_installed("blockchain"):
            try:
                from blockchain.models import Transaction as BlockchainTransaction
                from blockchain.models import SmartContract
                from blockchain.models import Block

                stats["total_transactions"] = BlockchainTransaction.objects.filter(
                    status="confirmed"
                ).count()
                stats["total_contracts"] = SmartContract.objects.filter(
                    is_active=True
                ).count()
                stats["total_blocks"] = Block.objects.count()
            except Exception:
                stats["total_transactions"] = 0
                stats["total_contracts"] = 0
                stats["total_blocks"] = 0

    elif page_key == "products_egitim":
        # Eğitim istatistikleri
        if apps.is_installed("education"):
            try:
                from education.models import Course, Certificate, Enrollment

                stats["total_courses"] = Course.objects.filter(is_active=True).count()
                stats["total_certificates"] = Certificate.objects.count()
                stats["total_enrollments"] = Enrollment.objects.count()
                user_model = get_user_model()
                stats["teacher_count"] = user_model.objects.filter(
                    user_type__code__in=["teacher", "egitimci"]
                ).count()
                stats["student_count"] = user_model.objects.filter(
                    user_type__code__in=["student", "ogrenci"]
                ).count()
            except Exception:
                stats["total_courses"] = 0
                stats["total_certificates"] = 0
                stats["total_enrollments"] = 0
                stats["teacher_count"] = 0
                stats["student_count"] = 0

    elif page_key == "products_oyunlar":
        # Oyunlar istatistikleri
        user_model = get_user_model()
        stats["player_count"] = user_model.objects.filter(
            user_type__code__in=["player", "oyuncu"]
        ).count()
        if apps.is_installed("games"):
            try:
                from games.models import GameSession, Leaderboard

                stats["total_sessions"] = GameSession.objects.count()
                stats["leaderboard_entries"] = Leaderboard.objects.count()
            except Exception:
                stats["total_sessions"] = 0
                stats["leaderboard_entries"] = 0

    elif page_key == "products_mali_musavir":
        # Mali Müşavirlik istatistikleri
        if apps.is_installed("advisors"):
            try:
                from advisors.models import (
                    AdvisorProfile,
                    TaxpayerProfile,
                    ConsultationSession,
                    AdvisorReport,
                )

                stats["verified_advisors"] = AdvisorProfile.objects.filter(
                    verified_at__isnull=False
                ).count()
                stats["total_clients"] = TaxpayerProfile.objects.count()
                stats["total_consultations"] = ConsultationSession.objects.count()
                stats["total_reports"] = AdvisorReport.objects.count()
            except Exception:
                stats["verified_advisors"] = 0
                stats["total_clients"] = 0
                stats["total_consultations"] = 0
                stats["total_reports"] = 0

        if apps.is_installed("partners"):
            try:
                from partners.models import PartnerProfile
                from django.db import connection
                from django.db.utils import OperationalError, ProgrammingError

                # Tablonun var olup olmadığını kontrol et
                table_name = PartnerProfile._meta.db_table
                with connection.cursor() as cursor:
                    if connection.vendor == "postgresql":
                        cursor.execute(
                            """
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = %s
                            );
                        """,
                            [table_name],
                        )
                        table_exists = cursor.fetchone()[0]
                    else:
                        table_exists = (
                            table_name in connection.introspection.table_names()
                        )

                if table_exists:
                    stats["partner_count"] = PartnerProfile.objects.filter(
                        status=PartnerProfile.Status.PUBLISHED
                    ).count()
                else:
                    stats["partner_count"] = 0
            except (OperationalError, ProgrammingError, Exception):
                stats["partner_count"] = 0

    elif page_key == "products_yapay_zeka":
        # Yapay Zeka istatistikleri
        try:
            stats["prompt_count"] = sum(
                len(prompt_registry.get_prompts_for_role(role))
                for role in prompt_registry.list_roles()
            )
            stats["ai_cards"] = len(
                prompt_registry.get_prompts_for_role("kobi", limit=10)
            )
        except Exception:
            stats["prompt_count"] = 0
            stats["ai_cards"] = 0

        if apps.is_installed("ai_assistant"):
            try:
                from ai_assistant.models import ChatSession, AIPrompt

                stats["chat_sessions"] = ChatSession.objects.count()
                stats["custom_prompts"] = AIPrompt.objects.count()
            except Exception:
                stats["chat_sessions"] = 0
                stats["custom_prompts"] = 0

    elif page_key == "products_kobi_analizi":
        # KOBİ Analizi istatistikleri
        stats["company_count"] = Company.objects.filter(is_active=True).count()
        if apps.is_installed("kobi_analysis"):
            try:
                from kobi_analysis.models import (
                    KOBIFinancialAnalysis,
                    FinancialReport,
                    FinancialGoal,
                )

                stats["total_analyses"] = KOBIFinancialAnalysis.objects.count()
                stats["total_reports"] = FinancialReport.objects.count()
                stats["active_goals"] = FinancialGoal.objects.filter(
                    status="IN_PROGRESS"
                ).count()
            except Exception:
                stats["total_analyses"] = 0
                stats["total_reports"] = 0
                stats["active_goals"] = 0

    elif page_key == "products_edonusum":
        # e-Dönüşüm istatistikleri
        stats["total_invoices"] = AccountingInvoice.objects.count()
        stats["company_count"] = Company.objects.filter(is_active=True).count()
        today = timezone.localdate()
        start_of_month = today.replace(day=1)
        monthly_invoices = AccountingInvoice.objects.filter(
            issue_date__gte=start_of_month,
            is_active=True,
        )
        stats["monthly_invoices"] = monthly_invoices.count()
        # e-fatura sayısı (örnek olarak tüm faturalar e-fatura kabul ediliyor)
        stats["e_invoice_count"] = AccountingInvoice.objects.filter(
            is_active=True
        ).count()

    elif page_key == "products_audit":
        # Denetim istatistikleri
        if apps.is_installed("audit"):
            try:
                from audit.models import AuditEvent, Control

                stats["audit_event_count"] = AuditEvent.objects.count()
                stats["control_count"] = Control.objects.filter(is_active=True).count()
            except Exception:
                stats["audit_event_count"] = 0
                stats["control_count"] = 0
        stats["company_count"] = Company.objects.filter(is_active=True).count()

    # Genel istatistikler (tüm sayfalar için)
    user_model = get_user_model()
    stats["total_active_users"] = user_model.objects.filter(is_active=True).count()
    stats["total_companies"] = Company.objects.filter(is_active=True).count()

    return stats


def marketing_page(request, page_key: str):
    """
    Tekrarlı pazarlama ve tanıtım sayfalarını render eden genel amaçlı görünüm.
    Dinamik istatistiklerle zenginleştirilmiş.
    """
    page_config = MARKETING_PAGES.get(page_key)
    if page_config is None:
        raise Http404(f"Marketing page config not found for key '{page_key}'.")

    # Ürün sayfası için dinamik istatistikleri hesapla
    product_stats = _get_product_stats(page_key)

    context: Dict[str, object] = {
        "page_config": page_config,
        "stats": product_stats,
    }
    if page_config.title:
        context.setdefault("page_title", page_config.title)
    if page_config.description:
        context.setdefault("page_description", page_config.description)

    return render(request, page_config.template_name, context)


def ui_components(request):
    """
    UI bileşenleri demo sayfası (geliştirme amaçlı)
    """
    context = {
        "page_title": _("UI Bileşenleri"),
    }
    return render(request, "core_ui/components.html", context)


def theme_demo(request):
    """
    Tema ve stil rehberi
    """
    context = {
        "page_title": _("Tema ve Stil Rehberi"),
    }
    return render(request, "core_ui/theme_demo.html", context)


def support_live(request):
    """
    Destek merkezi · Canlı destek sayfası.
    """
    context = {
        "page_title": _("Canlı Destek"),
    }
    return render(request, "support/live.html", context)


def support_faq(request):
    """
    Destek merkezi · Sıkça sorulan sorular sayfası.
    """
    context = {
        "page_title": _("Sıkça Sorulan Sorular"),
    }
    return render(request, "support/faq.html", context)


def support_tech(request):
    """
    Destek merkezi · Teknik yardım sayfası.
    """
    context = {
        "page_title": _("Teknik Yardım"),
    }
    return render(request, "support/tech.html", context)


def site_search(request):
    """
    Basit site içi arama (kurumsal içerikler + yardım bağlantıları)
    """
    query = request.GET.get("q", "").strip()
    results: List[Dict[str, str]] = []

    if query:
        press_hits = PressRelease.objects.filter(title__icontains=query)[:5]
        for press in press_hits:
            results.append(
                {
                    "title": press.title,
                    "snippet": Truncator(press.summary or "").chars(130)
                    or _("Kurumsal duyuru"),
                    "url": press.url or reverse("corporate:landing"),
                    "category": _("Basın Bülteni"),
                }
            )

        doc_hits = InvestorDocument.objects.filter(
            Q(name__icontains=query) | Q(kind__icontains=query)
        )[:5]
        for doc in doc_hits:
            results.append(
                {
                    "title": doc.name,
                    "snippet": (
                        _("Yatırımcı belgesi - {kind}").format(
                            kind=doc.get_kind_display()
                        )
                        if hasattr(doc, "get_kind_display")
                        else _("Yatırımcı belgesi")
                    ),
                    "url": doc.file_url,
                    "category": _("Yatırımcı Belgeleri"),
                }
            )

        if request.user.is_authenticated:
            try:
                from common.models import (
                    SupportTicket,
                )  # Local import to avoid circular
            except Exception:
                SupportTicket = None  # type: ignore

            if SupportTicket is not None:
                ticket_hits = SupportTicket.objects.filter(user=request.user).filter(
                    Q(subject__icontains=query) | Q(message__icontains=query)
                )[:3]
                for ticket in ticket_hits:
                    results.append(
                        {
                            "title": _("Destek Talebi #{id}").format(id=ticket.id),
                            "snippet": Truncator(ticket.message).chars(130),
                            "url": reverse("common:help_center"),
                            "category": _("Destek"),
                        }
                    )
    else:
        # No query provided; show önerilen bağlantılar
        results = [
            {
                "title": _("Kaynak Merkezi"),
                "snippet": _(
                    "Dokümantasyon, eğitim içerikleri ve destek rehberlerine göz atın."
                ),
                "url": reverse("resources"),
                "category": _("Önerilen"),
            },
            {
                "title": _("Kurumsal Çözümler"),
                "snippet": _(
                    "FinAsis ile işletmenizi nasıl dönüştürebileceğinizi keşfedin."
                ),
                "url": reverse("corporate:landing"),
                "category": _("Önerilen"),
            },
            {
                "title": _("İletişim"),
                "snippet": _("Satış ekibimizle iletişime geçerek demo talep edin."),
                "url": reverse("contact"),
                "category": _("Önerilen"),
            },
        ]

    suggestions: List[str] = []
    if query and not results:
        suggestions = [
            _("Farklı anahtar kelimeler deneyin."),
            _("Yardım merkezinde aramak için “yardım” kelimesini eklemeyi deneyin."),
            _("Bizimle iletişime geçerek destek talebi oluşturabilirsiniz."),
        ]

    context = {
        "page_title": _("Arama Sonuçları"),
        "query": query,
        "results": results,
        "result_count": len(results),
        "suggestions": suggestions,
    }
    return render(request, "core_ui/search_results.html", context)


def site_robots(request):
    """robots.txt çıktısı (statik template üzerinden).

    Arama motorları için basit ve güvenli bir robots.txt döner.
    """
    response = render(request, "robots.txt", content_type="text/plain")
    # Statik içerik, cache edilebilir
    response["Cache-Control"] = "public, max-age=3600"
    return response


@require_http_methods(["POST"])
def ajax_theme_toggle(request):
    """
    AJAX: Tema değiştirme (dark/light mode)
    """
    theme = request.POST.get("theme", "light")

    # Session'a kaydet
    request.session["theme"] = theme

    return JsonResponse(
        {"success": True, "theme": theme, "message": _("Tema başarıyla değiştirildi.")}
    )


@require_http_methods(["GET"])
def ajax_user_preferences(request):
    """
    AJAX: Kullanıcı UI tercihleri
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": _("Giriş yapmalısınız.")}, status=401
        )

    # Varsayılan tercihler
    preferences = {
        "theme": request.session.get("theme", "light"),
        "language": request.session.get("django_language", "tr"),
        "sidebar_collapsed": request.session.get("sidebar_collapsed", False),
    }

    return JsonResponse({"success": True, "preferences": preferences})


def error_404(request, exception=None):
    """
    Custom 404 error handler
    """
    return render(request, "404.html", status=404)


def error_500(request):
    """
    Custom 500 error handler
    Handles server errors gracefully with proper logging
    """
    import logging

    logger = logging.getLogger(__name__)

    # Log the error if we have exception info
    if hasattr(request, "_exception"):
        logger.exception(
            f"500 Error on {request.method} {request.path}", exc_info=request._exception
        )
    else:
        logger.error(f"500 Error on {request.method} {request.path} - No exception info available")

    # Try to render the custom error page
    try:
        return render(request, "500.html", status=500)
    except Exception:
        # If template rendering fails, return a simple error page
        logger.exception("Failed to render 500.html template")
        from django.http import HttpResponseServerError
        return HttpResponseServerError(
            "<h1>500 - Sunucu Hatası</h1>"
            "<p>Üzgünüz, bir hata oluştu. Lütfen daha sonra tekrar deneyin.</p>"
            "<p><a href='/'>Ana Sayfaya Dön</a></p>"
        )

        # Return a simple HTML error page
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Server Error</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                h1 { color: #dc2626; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <h1>Server Error</h1>
            <p>The server encountered an error and could not complete your request.</p>
            <p>Please try again in a few moments.</p>
            <p><a href="/">Return to Home</a></p>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type="text/html")
