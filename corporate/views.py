# -*- coding: utf-8 -*-
"""
Corporate Views
Kurumsal İşletme Yönetimi ve İletişim Görünümleri
"""
from decimal import Decimal
from typing import Dict, List

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import formats, timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.urls import reverse

from billing.models import Plan, Module as BillingModule
from accounting.models import Company
from accounting.models import Invoice as AccountingInvoice
from ai_assistant.services import prompt_registry
from games import task_engine

from .models import PressRelease, InvestorDocument

try:
    from partners.models import PartnerProfile
except Exception:  # pragma: no cover
    PartnerProfile = None  # type: ignore[assignment]


def _format_number(value):
    return formats.number_format(value, force_grouping=True)


def _build_corporate_snapshot():
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    user_model = get_user_model()
    company_qs = Company.objects.filter(is_active=True)

    company_count = company_qs.count()
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
    module_count = module_qs.count()

    plan_qs = (
        Plan.objects.filter(is_active=True)
        .prefetch_related("prices", "plan_modules__module")
        .order_by("audience", "name")
    )

    def _safe_reverse(name: str) -> str:
        try:
            return reverse(name)
        except Exception:
            return ""

    plan_tiles: List[Dict[str, object]] = []
    customer_segments: List[Dict[str, object]] = []
    for plan in plan_qs:
        active_prices = [price for price in plan.prices.all() if price.is_active]
        monthly_price = next(
            (price for price in active_prices if price.period == "month"), None
        )
        yearly_price = next(
            (price for price in active_prices if price.period == "year"), None
        )
        currency = (
            (monthly_price or yearly_price).currency
            if (monthly_price or yearly_price)
            else None
        )

        plan_modules_manager = getattr(plan, "plan_modules", None)
        sample_modules = []
        if plan_modules_manager is not None:
            sample_modules = [
                pm.module.name
                for pm in plan_modules_manager.all()[:3]
                if getattr(pm, "module", None) and pm.module.is_active
            ]

        plan_tiles.append(
            {
                "code": plan.code,
                "name": plan.name,
                "audience": plan.get_audience_display()
                if hasattr(plan, "get_audience_display")
                else plan.audience,
                "description": plan.description,
                "monthly_price": monthly_price.amount if monthly_price else None,
                "yearly_price": yearly_price.amount if yearly_price else None,
                "currency": currency,
                "modules": sample_modules,
            }
        )
        customer_segments.append(plan_tiles[-1])

    plan_count = len(plan_tiles)

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

    ai_spotlight = (
        prompt_registry.get_prompts_for_role("kobi", limit=1)
        + prompt_registry.get_prompts_for_role("mali_musavir", limit=1)
        + prompt_registry.get_prompts_for_role("egitimci", limit=1)
    )

    teacher_brief = task_engine.get_brief(audience="teacher")
    student_brief = task_engine.get_brief(audience="student")
    gamer_brief = task_engine.get_brief(audience="gamer")

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
            "href": _safe_reverse("games:quests_home") or _safe_reverse("games:index"),
        },
    ]

    partner_count = 0
    if PartnerProfile is not None:
        partner_count = PartnerProfile.objects.filter(
            status=PartnerProfile.Status.PUBLISHED
        ).count()

    press_releases = list(PressRelease.objects.all()[:3])
    investor_documents = list(InvestorDocument.objects.all()[:3])

    solutions = [
        {
            "code": "accounting-suite",
            "title": _("Muhasebe & Finans"),
            "icon": "bi-receipt",
            "description": _(
                "Fatura, tahsilat ve banka entegrasyonlarını tek akışta yönetin; e-fatura ve e-arşiv çıktıları üretin."
            ),
            "href": _safe_reverse("products_muhasebe"),
            "stats": [
                {"label": _("Aktif şirket"), "value": _format_number(company_count)},
                {
                    "label": _("Toplam fatura"),
                    "value": _format_number(AccountingInvoice.objects.count()),
                },
            ],
        },
        {
            "code": "compliance-blockchain",
            "title": _("Uyumluluk & Blockchain"),
            "icon": "bi-shield-lock",
            "description": _(
                "Blockchain kanıtı, AML kontrolleri ve denetim izi üretimi ile tüm işlemleri doğrulanabilir kılın."
            ),
            "href": _safe_reverse("products_blockchain"),
            "stats": [
                {"label": _("Onaylanan blockchain işlemi"), "value": _format_number(0)},
                {"label": _("Partner sayısı"), "value": _format_number(partner_count)},
            ],
        },
        {
            "code": "ai-assistant",
            "title": _("AI Asistan & Otomasyon"),
            "icon": "bi-robot",
            "description": _(
                "Rol bazlı Türkçe prompt kütüphanesi ve doğal dil rapor üretimiyle finans ekiplerini hızlandırın."
            ),
            "href": _safe_reverse("products_yapay_zeka"),
            "stats": [
                {
                    "label": _("Yayınlanan prompt"),
                    "value": _format_number(
                        sum(
                            len(prompt_registry.get_prompts_for_role(role))
                            for role in prompt_registry.list_roles()
                        )
                    ),
                },
                {
                    "label": _("Öne çıkan AI kartı"),
                    "value": _format_number(len(ai_spotlight)),
                },
            ],
        },
        {
            "code": "education-gamification",
            "title": _("Eğitim & Gamification"),
            "icon": "bi-mortarboard",
            "description": _(
                "FinQuest görev motoru ve öğretmen panoları ile oyunlaştırılmış finans eğitim deneyimi tasarlayın."
            ),
            "href": _safe_reverse("products_egitim"),
            "stats": [
                {
                    "label": _("Öğretmen görevleri"),
                    "value": _format_number(teacher_brief["task_count"]),
                },
                {
                    "label": _("Öğrenci görevleri"),
                    "value": _format_number(student_brief["task_count"]),
                },
            ],
        },
    ]

    resource_cards: List[Dict[str, object]] = []
    if press_releases:
        resource_cards.append(
            {
                "title": _("Basın & Duyurular"),
                "items": [
                    {
                        "label": release.title,
                        "meta": formats.date_format(release.date, "DATE_FORMAT"),
                        "href": release.url or "",
                    }
                    for release in press_releases
                ],
            }
        )
    if investor_documents:
        resource_cards.append(
            {
                "title": _("Yatırımcı Belgeleri"),
                "items": [
                    {
                        "label": doc.name,
                        "meta": formats.date_format(doc.published_at, "DATE_FORMAT")
                        if doc.published_at
                        else "",
                        "href": doc.file_url,
                    }
                    for doc in investor_documents
                ],
            }
        )
    if ai_spotlight:
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
            }
        )

    return {
        "metrics": metrics,
        "has_metrics_activity": has_metrics_activity,
        "hero_stats": metrics[:3],
        "solutions": solutions,
        "plan_tiles": plan_tiles[:3],
        "customer_segments": customer_segments,
        "journeys": journeys,
        "resource_cards": resource_cards,
        "press_releases": press_releases,
        "investor_documents": investor_documents,
        "ai_spotlight": ai_spotlight,
        "company_count": company_count,
        "active_user_count": active_user_count,
        "monthly_invoice_total": monthly_invoice_total,
        "monthly_invoice_count": monthly_invoice_count,
        "partner_count": partner_count,
    }


def corporate_landing(request):
    """
    Kurumsal merkez: şirket, yatırımcı, güvenlik ve sürdürülebilirlik sayfalarına giriş sayfası.
    """
    snapshot = _build_corporate_snapshot()

    context = {
        "page_title": _("Kurumsal Merkez"),
        **snapshot,
        "primary_navigation": [
            {"label": _("Genel Bakış"), "href": "#overview"},
            {"label": _("Şirket"), "href": "#company"},
            {"label": _("Yatırımcı & güvenlik"), "href": "#governance"},
            {"label": _("Kariyer"), "href": "#careers"},
            {"label": _("İletişim"), "href": "#contact"},
        ],
    }
    return render(request, "corporate/landing.html", context)


def contact(request):
    """
    Kurumsal iletişim ve satış ekibiyle bağlantı sayfası
    """
    from django.contrib import messages
    from django.core.mail import send_mail
    from django.conf import settings

    snapshot = _build_corporate_snapshot()

    try:
        partner_marketplace_url = reverse("resources_partner_marketplace")
    except Exception:
        partner_marketplace_url = ""

    # Form işleme
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        company = request.POST.get("company", "").strip()
        phone = request.POST.get("phone", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        privacy = request.POST.get("privacy")

        if not privacy:
            messages.error(request, _("KVKK onayı gereklidir."))
        elif not all([name, email, subject, message]):
            messages.error(request, _("Lütfen tüm zorunlu alanları doldurun."))
        else:
            # E-posta gönder
            subject_map = {
                "demo": _("Demo Talep"),
                "sales": _("Satış Bilgisi"),
                "support": _("Teknik Destek"),
                "compliance": _("Uyumluluk Danışmanlığı"),
                "partnership": _("Partner Olmak"),
                "other": _("Diğer"),
            }
            email_subject = f"[FinAsis İletişim] {subject_map.get(subject, _('İletişim Formu'))} - {name}"

            email_body = f"""
İletişim Formu Mesajı
====================

Ad Soyad: {name}
E-posta: {email}
Şirket: {company or 'Belirtilmemiş'}
Telefon: {phone or 'Belirtilmemiş'}
Konu: {subject_map.get(subject, subject)}

Mesaj:
{message}

---
Bu mesaj FinAsis iletişim formundan gönderilmiştir.
"""

            try:
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    ["sales@finasis.com"],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    _(
                        "Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız."
                    ),
                )
                return redirect(request.path + "?success=1")
            except Exception:
                messages.error(
                    request,
                    _(
                        "Mesaj gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin veya doğrudan e-posta gönderin."
                    ),
                )

    contact_channels = [
        {
            "icon": "bi-calendar-check",
            "title": _("Satış Ekibi ile Görüşün"),
            "description": _(
                "Ürünle ilgili sorularınızı iletin, kullanım senaryolarınızı bizimle paylaşın."
            ),
            "href": f"{request.build_absolute_uri()}?intent=demo",
            "cta": _("İletişime geçin"),
        },
        {
            "icon": "bi-clipboard-data",
            "title": _("Uyumluluk Danışmanlığı"),
            "description": _(
                "AML, KVKK ve MASAK gereksinimlerine özel danışman ekibi ile görüşün."
            ),
            "href": "#channels",
            "cta": _("Görüşme ayarla"),
        },
        {
            "icon": "bi-people",
            "title": _("Partner Ekosistemi"),
            "description": _(
                "FinAsis partner ağına katılın veya çözümlerimizi müşterilerinize sunun."
            ),
            "href": partner_marketplace_url,
            "cta": _("Partner merkezi"),
        },
    ]

    support_programs = snapshot["customer_segments"][:3]

    office_locations = [
        {
            "city": "İstanbul",
            "address": "Büyükdere Cad. No:123 Levent, Şişli/İstanbul",
            "phone": "+90 212 555 00 00",
        },
        {
            "city": "Ankara",
            "address": "Mustafa Kemal Mah. 2123. Cad. No:45 Çankaya/Ankara",
            "phone": "+90 312 555 00 00",
        },
    ]

    context = {
        "page_title": _("İletişim"),
        "sales_email": "sales@finasis.com",
        "support_email": "support@finasis.com",
        "phone_number": "+90 212 555 00 00",
        "office_locations": office_locations,
        "metrics": snapshot["hero_stats"],
        "has_metrics_activity": snapshot["has_metrics_activity"],
        "contact_channels": contact_channels,
        "support_programs": support_programs,
        "resource_cards": snapshot["resource_cards"],
        "primary_navigation": [
            {"label": _("İletişime geç"), "href": "#contact-hero"},
            {"label": _("Kanallar"), "href": "#channels"},
            {"label": _("Ofisler"), "href": "#offices"},
            {"label": _("Kaynaklar"), "href": "#resources"},
        ],
    }
    return render(request, "corporate/contact.html", context)


def about(request):
    """Kurumsal hakkımızda sayfası."""
    context = {
        "page_title": _("FinAsis · Hakkımızda"),
    }
    return render(request, "corporate/about.html", context)


def team(request):
    """Kurumsal ekip sayfası."""
    context = {
        "page_title": _("FinAsis · Ekip"),
    }
    return render(request, "corporate/team.html", context)


def careers(request):
    """Kariyer fırsatları sayfası."""
    context = {
        "page_title": _("FinAsis · Kariyer"),
    }
    return render(request, "corporate/careers.html", context)


def investors(request):
    """Yatırımcı ilişkileri sayfası."""
    from .models import InvestorDocument

    documents = list(InvestorDocument.objects.all())

    context = {
        "page_title": _("FinAsis · Yatırımcı İlişkileri"),
        "documents": documents,
    }
    return render(request, "corporate/investors.html", context)


def press(request):
    """Basın bültenleri sayfası."""
    context = {
        "page_title": _("FinAsis · Basın Merkezi"),
    }
    return render(request, "corporate/press.html", context)


def security_page(request):
    """Güvenlik ve uyumluluk sayfası."""
    context = {
        "page_title": _("FinAsis · Güvenlik"),
    }
    return render(request, "corporate/security.html", context)


def sustainability(request):
    """Sürdürülebilirlik ve ESG yaklaşımı sayfası."""
    context = {
        "page_title": _("FinAsis · Sürdürülebilirlik"),
    }
    return render(request, "corporate/sustainability.html", context)


@login_required
def corporate_dashboard(request):
    """
    Kurumsal müşteri yönetim dashboard'u (placeholder)
    """
    getattr(request.user, "company", None)

    context = {
        "clients": [],
        "total_clients": 0,
        "active_projects": [],
        "total_projects": 0,
        "active_contracts": [],
        "total_contracts": 0,
    }

    return render(request, "corporate/dashboard.html", context)


@login_required
def client_list(request):
    """Kurumsal müşteri listesi (placeholder)"""
    context = {"clients": []}
    return render(request, "corporate/client_list.html", context)


@login_required
def client_detail(request, client_id):
    """Kurumsal müşteri detay (placeholder)"""
    context = {
        "client": None,
        "contacts": [],
        "departments": [],
        "projects": [],
        "contracts": [],
    }
    return render(request, "corporate/client_detail.html", context)


@login_required
def client_create(request):
    """Yeni kurumsal müşteri (placeholder)"""
    if request.method == "POST":
        messages.info(request, _("Kurumsal müşteri modeli henüz aktif değil."))
        return redirect("corporate:client_list")

    context = {"industry_sectors": []}
    return render(request, "corporate/client_create.html", context)


@login_required
def project_list(request):
    """Kurumsal proje listesi (placeholder)"""
    context = {"projects": [], "status_filter": None}
    return render(request, "corporate/project_list.html", context)


@login_required
def project_detail(request, project_id):
    """Proje detay (placeholder)"""
    context = {"project": None}
    return render(request, "corporate/project_detail.html", context)


@login_required
def contract_list(request):
    """Sözleşme listesi (placeholder)"""
    context = {"contracts": []}
    return render(request, "corporate/contract_list.html", context)


@login_required
def ajax_client_stats(request):
    """AJAX: Müşteri istatistikleri (placeholder)"""
    stats = {
        "total_clients": 0,
        "active_projects": 0,
        "completed_projects": 0,
        "active_contracts": 0,
    }
    return JsonResponse({"success": True, "stats": stats})
