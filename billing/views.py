from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from .models import (
    Plan,
    Price,
    SubscriptionProfile,
    Transaction,
    BankTransfer,
    EnterpriseInquiry,
)
# PayTRClient ve RefGenerator billing/services.py'den import edilir
# services/ klasörü ile çakışmayı önlemek için doğrudan dosyadan import
import importlib.util
from pathlib import Path
services_file = Path(__file__).parent / "services.py"
spec = importlib.util.spec_from_file_location("billing_services_py", services_file)
billing_services_py = importlib.util.module_from_spec(spec)
spec.loader.exec_module(billing_services_py)
PayTRClient = billing_services_py.PayTRClient
RefGenerator = billing_services_py.RefGenerator
from decimal import Decimal, InvalidOperation
from typing import Optional, Iterable, Dict, List, Tuple
from django.utils import timezone
from django.utils.translation import gettext as _
from accounts.models import SubscriptionType, Subscription, SubscriptionLog
from django.contrib.auth.models import Group
from .models import PlanGroup
from accounting.models import Invoice, Customer
from django.core.mail import send_mail
import requests
from django.db.models import Prefetch
from django.db import IntegrityError, transaction

from .pricing import (
    build_plan_card,
    get_region_config,
    get_region_labels,
    get_supported_regions,
    resolve_region,
)


def _build_region_context(
    request: HttpRequest,
) -> Tuple[str, List[Dict[str, str]], Dict[str, object]]:
    region = resolve_region(request)
    supported = get_supported_regions()
    labels = get_region_labels()
    region_options = [
        {"code": code, "label": labels.get(code, code)} for code in supported
    ]
    region_config = get_region_config(region)
    return region, region_options, region_config


def _build_feature_rows(plans_list: Iterable[Plan]) -> List[Dict[str, object]]:
    module_to_plans: Dict[str, set[str]] = {}
    module_meta: Dict[str, str] = {}
    for plan in plans_list:
        for pm in getattr(plan, "plan_modules").all():
            module = getattr(pm, "module", None)
            if module is None:
                continue
            name = getattr(module, "name", None)
            if not name:
                continue
            module_to_plans.setdefault(name, set()).add(plan.code)
            description = getattr(module, "description", "") or ""
            if name not in module_meta and description:
                module_meta[name] = description
    feature_rows: List[Dict[str, object]] = []
    for name, codes in sorted(module_to_plans.items(), key=lambda x: x[0].lower()):
        feature_rows.append(
            {
                "name": name,
                "desc": module_meta.get(name, ""),
                "included": sorted(list(codes)),
            }
        )
    return feature_rows


def _prepare_plan_display(
    plans_list: List[Plan], region: str
) -> Tuple[
    List[Dict[str, object]], Dict[str, Dict[str, object]], List[Dict[str, object]]
]:
    card_map: Dict[str, Dict[str, object]] = {}
    popular_code: Optional[str] = None
    max_modules = -1
    for plan in plans_list:
        try:
            mod_count = getattr(plan, "plan_modules").all().count()
        except Exception:
            mod_count = 0
        if mod_count > max_modules:
            max_modules = mod_count
            popular_code = plan.code
        plan_prices = list(getattr(plan, "prices").all())
        card_map[plan.code] = build_plan_card(plan, region, prices=plan_prices)
    if popular_code and popular_code in card_map:
        card_map[popular_code]["popular"] = True
    plan_cards = [
        {"plan": plan, "card": card_map.get(plan.code)} for plan in plans_list
    ]
    feature_rows = _build_feature_rows(plans_list)
    return plan_cards, card_map, feature_rows


def plans_index(request: HttpRequest) -> HttpResponse:
    """Ana planlar sayfası - kategori seçimi, dinamik fiyat aralıkları ile."""
    region, region_options, region_config = _build_region_context(request)
    price_qs = Price.objects.filter(is_active=True).order_by("period")

    price_ranges: Dict[str, Dict[str, object]] = {}
    audience_map = {
        "sme": "kobi",
        "edu": "education",
        "games": "games",
    }

    for audience, key in audience_map.items():
        qs = Plan.objects.filter(is_active=True, audience=audience).prefetch_related(
            Prefetch("prices", queryset=price_qs),
            "plan_modules__module",
        )
        plans_list = list(qs)
        amounts = []
        currency = None
        for plan in plans_list:
            card = build_plan_card(plan, region, prices=getattr(plan, "prices").all())
            month_amount = card.get("month_amount")
            if month_amount is not None:
                amounts.append(month_amount)
                currency = card.get("currency") or currency
        if amounts and currency:
            price_ranges[key] = {
                "min": min(amounts),
                "max": max(amounts),
                "currency": currency,
            }

    context = {
        "region": region,
        "region_options": region_options,
        "region_config": region_config,
        "price_ranges": price_ranges,
    }
    return render(request, "billing/plans_index.html", context)


def plans_kobi(request: HttpRequest) -> HttpResponse:
    """KOBİ planları - Özel tasarım"""
    period = request.GET.get("period", "month")
    region, region_options, region_config = _build_region_context(request)
    price_qs = Price.objects.filter(is_active=True).order_by("period")
    qs = Plan.objects.filter(is_active=True, audience="sme").prefetch_related(
        Prefetch("prices", queryset=price_qs), "plan_modules__module"
    )
    plans_list = list(qs)

    order_cfg = getattr(settings, "BILLING_PLAN_ORDER", {})
    sme_order = order_cfg.get("sme", ["starter", "sme_pro", "sme_enterprise"])
    order_map = {code: i + 1 for i, code in enumerate(sme_order)}
    plans_list.sort(
        key=lambda p: (
            order_map.get(getattr(p, "code", ""), 999),
            getattr(p, "name", "").lower(),
        )
    )

    plan_cards, card_map, feature_rows = _prepare_plan_display(plans_list, region)

    return render(
        request,
        "billing/plans_kobi.html",
        {
            "plans": plans_list,
            "plan_cards": plan_cards,
            "period": period,
            "feature_rows": feature_rows,
            "card_map": card_map,
            "region": region,
            "region_options": region_options,
            "region_config": region_config,
        },
    )


def plans_education(request: HttpRequest) -> HttpResponse:
    """Eğitim planları - Özel tasarım"""
    period = request.GET.get("period", "month")
    region, region_options, region_config = _build_region_context(request)
    price_qs = Price.objects.filter(is_active=True).order_by("period")
    qs = Plan.objects.filter(is_active=True, audience="edu").prefetch_related(
        Prefetch("prices", queryset=price_qs), "plan_modules__module"
    )
    plans_list = list(qs)

    order_cfg = getattr(settings, "BILLING_PLAN_ORDER", {})
    edu_order = order_cfg.get("edu", ["edu_student", "edu_teacher", "edu_campus"])
    order_map = {code: i + 1 for i, code in enumerate(edu_order)}
    plans_list.sort(
        key=lambda p: (
            order_map.get(getattr(p, "code", ""), 999),
            getattr(p, "name", "").lower(),
        )
    )

    plan_cards, card_map, feature_rows = _prepare_plan_display(plans_list, region)

    return render(
        request,
        "billing/plans_education.html",
        {
            "plans": plans_list,
            "plan_cards": plan_cards,
            "period": period,
            "feature_rows": feature_rows,
            "card_map": card_map,
            "region": region,
            "region_options": region_options,
            "region_config": region_config,
        },
    )


def plans_games(request: HttpRequest) -> HttpResponse:
    """Oyuncu planları - Özel tasarım"""
    period = request.GET.get("period", "month")
    region, region_options, region_config = _build_region_context(request)
    price_qs = Price.objects.filter(is_active=True).order_by("period")
    qs = Plan.objects.filter(is_active=True, audience="games").prefetch_related(
        Prefetch("prices", queryset=price_qs), "plan_modules__module"
    )
    plans_list = list(qs)

    order_cfg = getattr(settings, "BILLING_PLAN_ORDER", {})
    games_order = order_cfg.get("games", ["games_free", "games_pro", "games_elite"])
    order_map = {code: i + 1 for i, code in enumerate(games_order)}
    plans_list.sort(
        key=lambda p: (
            order_map.get(getattr(p, "code", ""), 999),
            getattr(p, "name", "").lower(),
        )
    )

    plan_cards, card_map, feature_rows = _prepare_plan_display(plans_list, region)

    return render(
        request,
        "billing/plans_games.html",
        {
            "plans": plans_list,
            "plan_cards": plan_cards,
            "period": period,
            "feature_rows": feature_rows,
            "card_map": card_map,
            "region": region,
            "region_options": region_options,
            "region_config": region_config,
        },
    )


def plans_by_category(
    request: HttpRequest, audience: str, category_name: str
) -> HttpResponse:
    """Kategori-specific planlar sayfası"""
    period = request.GET.get("period")
    if period not in ("month", "year"):
        period = "month"
    region, region_options, region_config = _build_region_context(request)
    price_qs = Price.objects.filter(is_active=True).order_by("period")
    qs = Plan.objects.filter(is_active=True).prefetch_related(
        Prefetch("prices", queryset=price_qs), "plan_modules__module"
    )
    if audience in ("sme", "edu", "games"):
        qs = qs.filter(audience=audience)
    plans_list = list(qs)
    # Mantıklı sıralama: SME için Starter→Pro→Enterprise; EDU için Student→Teacher→Campus
    # Configurable plan order via settings, with safe defaults
    order_cfg = getattr(
        settings,
        "BILLING_PLAN_ORDER",
        {
            "sme": ["starter", "sme_pro", "sme_enterprise"],
            "edu": ["edu_student", "edu_teacher", "edu_campus"],
            "games": ["games_free", "games_pro", "games_elite"],
        },
    )
    if audience == "sme":
        order_map = {code: i + 1 for i, code in enumerate(order_cfg.get("sme", []))}
    elif audience == "edu":
        order_map = {code: i + 1 for i, code in enumerate(order_cfg.get("edu", []))}
    elif audience == "games":
        order_map = {code: i + 1 for i, code in enumerate(order_cfg.get("games", []))}
    else:
        # combine all with different buckets
        sme_map = {code: i + 1 for i, code in enumerate(order_cfg.get("sme", []))}
        edu_map = {code: 10 + i + 1 for i, code in enumerate(order_cfg.get("edu", []))}
        games_map = {
            code: 20 + i + 1 for i, code in enumerate(order_cfg.get("games", []))
        }
        order_map = {**sme_map, **edu_map, **games_map}
    plans_list.sort(
        key=lambda p: (
            order_map.get(getattr(p, "code", ""), 999),
            getattr(p, "name", "").lower(),
        )
    )

    plan_cards, card_map, feature_rows = _prepare_plan_display(plans_list, region)

    module_meta = {row["name"]: row.get("desc", "") for row in feature_rows}
    module_to_plans = {
        row["name"]: set(row.get("included", [])) for row in feature_rows
    }

    # Öne çıkan modüller (audience'a göre vitrin)
    # Featured modules configurable via settings with sensible defaults
    feat_cfg = getattr(
        settings,
        "BILLING_FEATURED_MODULES",
        {
            "sme": [
                "e-Fatura",
                "Nakit Akışı",
                "Banka Entegrasyonları",
                "AI Destekli Analiz",
            ],
            "edu": [
                "Eğitim/LMS",
                "Analitik & Gelişmiş Raporlama",
                "AI Destekli Analiz",
            ],
        },
    )
    if audience == "edu":
        featured_names = list(feat_cfg.get("edu", []))
    elif audience == "games":
        featured_names = list(feat_cfg.get("games", feat_cfg.get("sme", [])))
    else:
        featured_names = list(feat_cfg.get("sme", []))
    featured_badges = [
        {"name": name, "desc": module_meta.get(name, "")}
        for name in featured_names
        if name in module_to_plans  # sadece var olan modülleri göster
    ]
    region_currency = region_config.get(
        "currency", getattr(settings, "BASE_PRICING_CURRENCY", "TRY")
    )
    region_tax_summary = None
    if "vat_rate" in region_config:
        try:
            rate = Decimal(str(region_config["vat_rate"])) * Decimal("100")
            region_tax_summary = _("KDV oranı %(rate)s%%") % {
                "rate": rate.quantize(Decimal("0.01"))
            }
        except (InvalidOperation, ValueError):
            region_tax_summary = _("KDV uygulanır.")
    elif "gst_rate" in region_config:
        try:
            rate = Decimal(str(region_config["gst_rate"])) * Decimal("100")
            region_tax_summary = _("GST oranı %(rate)s%%") % {
                "rate": rate.quantize(Decimal("0.01"))
            }
        except (InvalidOperation, ValueError):
            region_tax_summary = _("GST uygulanır.")
    elif region_config.get("sales_tax"):
        region_tax_summary = _("Satış vergisi: %(note)s") % {
            "note": region_config["sales_tax"]
        }
    return render(
        request,
        "billing/plans_category.html",
        {
            "plans": plans_list,
            "plan_cards": plan_cards,
            "audience": audience or "sme",
            "category_name": category_name,
            "period": period,
            "feature_rows": feature_rows,
            "BANK_TRANSFER_ENABLED": getattr(settings, "BANK_TRANSFER_ENABLED", True),
            "card_map": card_map,
            "featured_badges": featured_badges,
            "region": region,
            "region_options": region_options,
            "region_config": region_config,
            "region_currency": region_currency,
            "region_tax_summary": region_tax_summary,
            "region_query": f"region={region}",
        },
    )


def plans(request: HttpRequest) -> HttpResponse:
    """Ana planlar sayfası - kategori seçimi"""
    return render(request, "billing/plans_index.html")


@login_required
def select_plan(request: HttpRequest, plan_code: str) -> HttpResponse:
    plan = Plan.objects.filter(code=plan_code, is_active=True).first()
    if not plan:
        return redirect("billing:plans")
    # Periyot tercihi: ?period=month|year, varsayılan: aylık (mevcut değilse yıllık)
    preferred = request.GET.get("period")
    qs = Price.objects.filter(plan=plan, is_active=True)
    price = None
    if preferred in ("month", "year"):
        price = qs.filter(period=preferred).first()
    if not price:
        price = qs.filter(period="month").first() or qs.filter(period="year").first()
    if not price:
        return redirect("billing:plans")
    price_id = getattr(price, "pk", getattr(price, "id", None))
    if not price_id:
        return redirect("billing:plans")
    return redirect("billing:checkout_paytr", price_id=price_id)


@login_required
def enterprise_inquiry(request: HttpRequest, plan_code: str) -> HttpResponse:
    plan = Plan.objects.filter(code=plan_code).first()
    if request.method == "POST":
        # request.user Anonymous olabilir; güvenli çek
        user_full_name = getattr(request.user, "get_full_name", None)
        resolved_full_name = user_full_name() if callable(user_full_name) else ""
        safe_username = getattr(request.user, "username", "") or ""
        name = request.POST.get("name") or (resolved_full_name or safe_username)
        email = request.POST.get("email") or getattr(request.user, "email", "") or ""
        company = request.POST.get("company", "")
        phone = request.POST.get("phone", "")
        message = request.POST.get("message", "")
        EnterpriseInquiry.objects.create(
            user=request.user,
            plan=plan,
            name=name,
            email=email,
            company=company,
            phone=phone,
            message=message,
        )
        # Email bildirimi
        try:
            send_mail(
                subject=f"Enterprise Talebi: {plan.name if plan else ''}",
                message=f"Ad: {name}\nEmail: {email}\nŞirket: {company}\nTelefon: {phone}\nMesaj: {message}",
                from_email=None,
                recipient_list=[
                    getattr(settings, "SALES_EMAIL", "sales@finasis.local")
                ],
                fail_silently=True,
            )
        except Exception:
            pass
        # Slack bildirimi (opsiyonel)
        try:
            hook = getattr(settings, "SLACK_WEBHOOK_URL", "")
            if hook:
                payload = {
                    "text": f"Yeni Enterprise Talebi: {name} | {email} | {company} | {phone} | Plan: {plan.name if plan else ''}"
                }
                requests.post(hook, json=payload, timeout=5)
        except Exception:
            pass
        return render(
            request,
            "billing/thanks.html",
            {
                "title": "Teşekkürler",
                "message": "Talebinizi aldık. En kısa sürede iletişime geçeceğiz.",
            },
        )
    return render(request, "billing/enterprise_inquiry.html", {"plan": plan})


@login_required
def checkout_paytr(request: HttpRequest, price_id: int) -> HttpResponse:
    price = Price.objects.select_related("plan").get(id=price_id, is_active=True)
    user = request.user
    amount_kurus = int(price.amount * 100)
    # Basit sepet örneği (PayTR base64 JSON sepet)
    import json
    import base64

    basket = base64.b64encode(
        json.dumps([[price.plan.name, str(price.amount), 1]]).encode("utf-8")
    ).decode("utf-8")

    user_email = getattr(user, "email", None) or "user@example.com"
    payload = {
        "merchant_id": getattr(settings, "PAYTR_MERCHANT_ID", ""),
        "user_ip": request.META.get("REMOTE_ADDR", "127.0.0.1"),
        "merchant_oid": f"OID{getattr(user, 'id', 0)}{int(timezone.now().timestamp())}",
        "email": user_email,
        "payment_amount": amount_kurus,
        "user_basket_b64": basket,
        "no_installment": 0,
        "max_installment": 12,
        "currency": "TL",
        "test_mode": 1 if getattr(settings, "PAYTR_SANDBOX", True) else 0,
    }
    resp = PayTRClient.init_payment(payload)
    trx = Transaction.objects.create(
        user=user,
        plan=price.plan,
        price=price,
        amount=price.amount,
        currency=price.currency,
        method="paytr",
        status="initiated",
        external_id=payload.get("merchant_oid", ""),
        meta=payload,
    )
    if resp.get("status") == "success":
        return render(
            request,
            "billing/paytr_iframe.html",
            {"iframe_token": resp["iframe_token"], "transaction": trx},
        )
    return render(request, "billing/error.html", {"message": "Ödeme başlatılamadı."})


@csrf_exempt
@require_POST
def paytr_callback(request: HttpRequest) -> HttpResponse:
    # PayTR server-to-server callback (ödeme sonucu)
    merchant_oid = request.POST.get("merchant_oid") or ""
    status = request.POST.get("status") or ""
    total_amount = request.POST.get("total_amount") or ""
    hash_str = request.POST.get("hash") or ""
    client_ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get(
        "REMOTE_ADDR"
    )
    if not PayTRClient.verify_callback(
        merchant_oid, status, total_amount, hash_str, request_ip=client_ip
    ):
        return HttpResponse("OK")  # PayTR yeniden denemesin
    # merchant_oid ile ilgili işlemi bul
    trx = (
        Transaction.objects.filter(method="paytr", external_id=merchant_oid)
        .order_by("-id")
        .first()
    )
    if not trx:
        return HttpResponse("OK")
    if status == "success":
        trx.status = "paid"
        trx.save(update_fields=["status"])
        _activate_subscription(trx.user, trx.plan, trx.price)
        _create_invoice_for_subscription(trx)
    else:
        trx.status = "failed"
        trx.save(update_fields=["status"])
    return HttpResponse("OK")


@login_required
def checkout_bank_transfer(request: HttpRequest, price_id: int) -> HttpResponse:
    price = Price.objects.select_related("plan").get(id=price_id, is_active=True)
    # Benzersiz referans üretimi (çakışma halinde yeniden dene)
    ref = None
    for _attempt in range(5):
        try:
            ref_candidate = RefGenerator.bank_reference()
            with transaction.atomic():
                BankTransfer.objects.create(
                    user=request.user,
                    plan=price.plan,
                    price=price,
                    amount=price.amount,
                    currency=price.currency,
                    reference_code=ref_candidate,
                )
            ref = ref_candidate
            break
        except IntegrityError:
            continue
    if not ref:
        return render(
            request,
            "billing/error.html",
            {"message": "İşlem oluşturulamadı. Lütfen tekrar deneyin."},
            status=500,
        )
    ctx = {
        "price": price,
        "ref": ref,
        "bank_holder": getattr(settings, "BANK_ACCOUNT_HOLDER", ""),
        "bank_iban": getattr(settings, "BANK_ACCOUNT_IBAN", ""),
        "bank_name": getattr(settings, "BANK_ACCOUNT_BANK", ""),
    }
    return render(request, "billing/bank_transfer.html", ctx)


@login_required
def portal(request: HttpRequest) -> HttpResponse:
    profile, _ = SubscriptionProfile.objects.get_or_create(user=request.user)
    trx = Transaction.objects.filter(user=request.user).order_by("-created_at")[:20]
    bank = BankTransfer.objects.filter(user=request.user).order_by("-created_at")[:20]
    return render(
        request,
        "billing/portal.html",
        {"profile": profile, "transactions": trx, "bank_transfers": bank},
    )


@staff_member_required(login_url="/accounts/login/")
def admin_confirm_bank_transfer(
    request: HttpRequest, reference_code: str
) -> HttpResponse:
    bt = BankTransfer.objects.get(reference_code=reference_code, is_confirmed=False)
    bt.confirm()
    _activate_subscription(bt.user, bt.plan, bt.price)
    # Create invoice after bank confirmation
    _create_invoice_for_subscription(None, bank_transfer=bt)
    return redirect("billing:portal")


def _activate_subscription(user, plan, price):
    profile, _ = SubscriptionProfile.objects.get_or_create(user=user)
    previous_plan = profile.plan
    profile.plan = plan
    profile.status = "active"
    # Periyoda göre dönem
    if price.period == "month":
        profile.current_period_end = timezone.now() + timezone.timedelta(days=30)
    else:
        profile.current_period_end = timezone.now() + timezone.timedelta(days=365)
    profile.save()
    
    # Blockchain sözleşme oluştur (10.000₺+ veya beta üye ise)
    try:
        from billing.services.blockchain_contract import SubscriptionBlockchainService
        from billing.services.notification_service import BillingNotificationService
        
        contract_result = SubscriptionBlockchainService.create_subscription_contract(profile)
        
        if contract_result and contract_result.get("contract"):
            BillingNotificationService.send_contract_notification(
                user,
                contract_result["contract"]
            )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Blockchain sözleşme oluşturma hatası: {e}", exc_info=True)

    # Eski Accounts abonelik tipi ile uyumlu loglama (opsiyonel köprü)
    # Varsa aynı isimli SubscriptionType'a eşle
    try:
        stype = SubscriptionType.objects.filter(code__iexact=plan.code).first()
        if stype:
            acc_sub, _ = Subscription.objects.get_or_create(
                user=user, defaults={"subscription_type": stype}
            )
            old_type = acc_sub.subscription_type
            acc_sub.subscription_type = stype
            acc_sub.save(update_fields=["subscription_type"])
            SubscriptionLog.objects.create(
                user=user,
                old_subscription=old_type,
                new_subscription=stype,
                note="Billing activation",
            )
    except Exception:
        pass

    # Plan → Group atama
    try:
        if previous_plan and getattr(previous_plan, "id", None) != getattr(
            plan, "id", None
        ):
            old_groups = PlanGroup.objects.filter(plan=previous_plan).values_list(
                "group_id", flat=True
            )
            if old_groups:
                user.groups.remove(*Group.objects.filter(id__in=old_groups))
        new_groups = PlanGroup.objects.filter(plan=plan).values_list(
            "group_id", flat=True
        )
        if new_groups:
            user.groups.add(*Group.objects.filter(id__in=new_groups))
    except Exception:
        pass


def _create_invoice_for_subscription(trx=None, bank_transfer=None):
    try:
        source = trx or bank_transfer
        if not source:
            return
        user = getattr(source, "user", None)
        plan = getattr(source, "plan", None)
        price = getattr(source, "price", None)
        if not (user and plan and price):
            return
        company = getattr(user, "company", None)
        if not company:
            return
        # Customer yoksa kullanıcıya müşteri oluştur
        cust, _ = Customer.objects.get_or_create(
            company=company,
            email=user.email or "",
            defaults={
                "first_name": user.first_name or user.username,
                "last_name": user.last_name or "",
            },
        )
        period_label = (
            "Aylık" if getattr(price, "period", "month") == "month" else "Yıllık"
        )
        Invoice.objects.create(
            company=company,
            customer=cust,
            invoice_number=f"SUB-{int(timezone.now().timestamp())}",
            issue_date=timezone.now().date(),
            total_amount=price.amount,
            currency=price.currency,
            description=f"{getattr(plan, 'name', 'Plan')} {period_label} abonelik ücreti",
        )
    except Exception:
        # Sessiz geç; ileride logla
        pass
