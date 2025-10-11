from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from .models import Plan, Price, SubscriptionProfile, Transaction, BankTransfer, EnterpriseInquiry
from .services import PayTRClient, RefGenerator
from decimal import Decimal, InvalidOperation
from typing import Optional, cast
from django.utils import timezone
from src.apps.accounts.models import SubscriptionType, Subscription, SubscriptionLog
from django.contrib.auth.models import Group
from .models import PlanGroup
from src.apps.accounting.models import Invoice, Customer, Company
from django.core.mail import send_mail
import requests
from django.db.models import Prefetch
from django.db import IntegrityError, transaction

def plans(request: HttpRequest) -> HttpResponse:
    audience = request.GET.get('audience')  # 'sme' | 'edu' | None
    period = request.GET.get('period')  # 'month' | 'year' | None
    price_qs = Price.objects.filter(is_active=True).order_by('period')
    qs = (
        Plan.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch('prices', queryset=price_qs),
            'plan_modules__module'
        )
    )
    if audience in ('sme', 'edu'):
        qs = qs.filter(audience=audience)
    plans_list = list(qs)

    # Türkiye odaklı ek bağlam: KDV, taksit, yıllık indirim vb.
    VAT_INCLUDED = getattr(settings, 'VAT_INCLUDED', True)
    try:
        VAT_RATE = int(getattr(settings, 'VAT_RATE', 20))
    except Exception:
        VAT_RATE = 20
    try:
        INSTALLMENT_MAX = int(getattr(settings, 'INSTALLMENT_MAX', 12))
    except Exception:
        INSTALLMENT_MAX = 12

    # Plan -> fiyat eşlemeleri ve popüler plan belirleme (özellik sayısına göre)
    card_map: dict[str, dict] = {}
    popular_code: str | None = None
    max_modules = -1
    for p in plans_list:
        # Modül sayısına göre popüler plan heuristiği
        try:
            mod_count = getattr(p, 'plan_modules').all().count()
        except Exception:
            mod_count = 0
        if mod_count > max_modules:
            max_modules = mod_count
            popular_code = p.code

        month_price = None
        year_price = None
        for pr in getattr(p, 'prices').all():
            if getattr(pr, 'period', '') == 'month' and month_price is None:
                month_price = pr
            if getattr(pr, 'period', '') == 'year' and year_price is None:
                year_price = pr

        month_amount = cast(Optional[Decimal], getattr(month_price, 'amount', None))
        year_amount = cast(Optional[Decimal], getattr(year_price, 'amount', None))
        year_per_month: Optional[Decimal] = None
        discount_pct: Optional[float] = None
        try:
            if year_amount is not None:
                # Ay eşdeğeri: yıllık/12
                year_per_month = (year_amount / Decimal('12'))
            if month_amount is not None and year_amount is not None and month_amount > 0:
                discount_pct = float(100 * (1 - (year_amount / (month_amount * Decimal('12')))))
        except (InvalidOperation, ZeroDivisionError):
            year_per_month = None
            discount_pct = None

        card_map[p.code] = {
            'month_amount': month_amount,
            'year_amount': year_amount,
            'year_per_month': year_per_month,
            'discount_pct': discount_pct,
            'currency': getattr(month_price or year_price, 'currency', 'TL'),
            'has_month': month_price is not None,
            'has_year': year_price is not None,
            'popular': False,  # fill after loop
        }
    if popular_code and popular_code in card_map:
        card_map[popular_code]['popular'] = True
    module_to_plans = {}
    for p in plans_list:
        for pm in getattr(p, 'plan_modules').all():
            mname = getattr(pm.module, 'name', None)
            if not mname:
                continue
            module_to_plans.setdefault(mname, set()).add(p.code)
    feature_rows = [
        {
            'name': name,
            'included': sorted(list(codes)),
        }
        for name, codes in sorted(module_to_plans.items(), key=lambda x: x[0].lower())
    ]
    plan_cards = [{'plan': p, 'card': card_map.get(p.code)} for p in plans_list]
    return render(request, 'billing/plans.html', {
        'plans': plans_list,
        'plan_cards': plan_cards,
        'audience': audience or 'sme',
        'period': period or 'month',
        'feature_rows': feature_rows,
        'BANK_TRANSFER_ENABLED': getattr(settings, 'BANK_TRANSFER_ENABLED', True),
        'VAT_INCLUDED': VAT_INCLUDED,
        'VAT_RATE': VAT_RATE,
        'INSTALLMENT_MAX': INSTALLMENT_MAX,
        'card_map': card_map,
    })

@login_required
def select_plan(request: HttpRequest, plan_code: str) -> HttpResponse:
    plan = Plan.objects.filter(code=plan_code, is_active=True).first()
    if not plan:
        return redirect('billing:plans')
    # Periyot tercihi: ?period=month|year, varsayılan: aylık (mevcut değilse yıllık)
    preferred = request.GET.get('period')
    qs = Price.objects.filter(plan=plan, is_active=True)
    price = None
    if preferred in ('month', 'year'):
        price = qs.filter(period=preferred).first()
    if not price:
        price = qs.filter(period='month').first() or qs.filter(period='year').first()
    if not price:
        return redirect('billing:plans')
    price_id = getattr(price, 'pk', getattr(price, 'id', None))
    if not price_id:
        return redirect('billing:plans')
    return redirect('billing:checkout_paytr', price_id=price_id)

@login_required
def enterprise_inquiry(request: HttpRequest, plan_code: str) -> HttpResponse:
    plan = Plan.objects.filter(code=plan_code).first()
    if request.method == 'POST':
        # request.user Anonymous olabilir; güvenli çek
        user_full_name = getattr(request.user, 'get_full_name', None)
        resolved_full_name = user_full_name() if callable(user_full_name) else ''
        safe_username = getattr(request.user, 'username', '') or ''
        name = request.POST.get('name') or (resolved_full_name or safe_username)
        email = request.POST.get('email') or getattr(request.user, 'email', '') or ''
        company = request.POST.get('company', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')
        inquiry = EnterpriseInquiry.objects.create(
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
                recipient_list=[getattr(settings, 'SALES_EMAIL', 'sales@finasis.local')],
                fail_silently=True,
            )
        except Exception:
            pass
        # Slack bildirimi (opsiyonel)
        try:
            hook = getattr(settings, 'SLACK_WEBHOOK_URL', '')
            if hook:
                payload = {"text": f"Yeni Enterprise Talebi: {name} | {email} | {company} | {phone} | Plan: {plan.name if plan else ''}"}
                requests.post(hook, json=payload, timeout=5)
        except Exception:
            pass
        return render(request, 'billing/thanks.html', {'title': 'Teşekkürler', 'message': 'Talebinizi aldık. En kısa sürede iletişime geçeceğiz.'})
    return render(request, 'billing/enterprise_inquiry.html', {'plan': plan})

@login_required
def checkout_paytr(request: HttpRequest, price_id: int) -> HttpResponse:
    price = Price.objects.select_related('plan').get(id=price_id, is_active=True)
    user = request.user
    amount_kurus = int(price.amount * 100)
    # Basit sepet örneği (PayTR base64 JSON sepet)
    import json, base64
    basket = base64.b64encode(json.dumps([[price.plan.name, str(price.amount), 1]]).encode('utf-8')).decode('utf-8')

    user_email = getattr(user, 'email', None) or 'user@example.com'
    payload = {
        'merchant_id': getattr(settings, 'PAYTR_MERCHANT_ID', ''),
        'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'merchant_oid': f"OID{getattr(user, 'id', 0)}{int(timezone.now().timestamp())}",
        'email': user_email,
        'payment_amount': amount_kurus,
        'user_basket_b64': basket,
        'no_installment': 0,
        'max_installment': 12,
        'currency': 'TL',
        'test_mode': 1 if getattr(settings, 'PAYTR_SANDBOX', True) else 0,
    }
    resp = PayTRClient.init_payment(payload)
    trx = Transaction.objects.create(
        user=user,
        plan=price.plan,
        price=price,
        amount=price.amount,
        currency=price.currency,
        method='paytr',
        status='initiated',
        external_id=payload.get('merchant_oid', ''),
        meta=payload,
    )
    if resp.get('status') == 'success':
        return render(request, 'billing/paytr_iframe.html', {'iframe_token': resp['iframe_token'], 'transaction': trx})
    return render(request, 'billing/error.html', {'message': 'Ödeme başlatılamadı.'})

@csrf_exempt
@require_POST
def paytr_callback(request: HttpRequest) -> HttpResponse:
    # PayTR server-to-server callback (ödeme sonucu)
    merchant_oid = request.POST.get('merchant_oid') or ''
    status = request.POST.get('status') or ''
    total_amount = request.POST.get('total_amount') or ''
    hash_str = request.POST.get('hash') or ''
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    if not PayTRClient.verify_callback(merchant_oid, status, total_amount, hash_str, request_ip=client_ip):
        return HttpResponse('OK')  # PayTR yeniden denemesin
    # merchant_oid ile ilgili işlemi bul
    trx = Transaction.objects.filter(method='paytr', external_id=merchant_oid).order_by('-id').first()
    if not trx:
        return HttpResponse('OK')
    if status == 'success':
        trx.status = 'paid'
        trx.save(update_fields=['status'])
        _activate_subscription(trx.user, trx.plan, trx.price)
        _create_invoice_for_subscription(trx)
    else:
        trx.status = 'failed'
        trx.save(update_fields=['status'])
    return HttpResponse('OK')

@login_required
def checkout_bank_transfer(request: HttpRequest, price_id: int) -> HttpResponse:
    price = Price.objects.select_related('plan').get(id=price_id, is_active=True)
    # Benzersiz referans üretimi (çakışma halinde yeniden dene)
    ref = None
    for _ in range(5):
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
        return render(request, 'billing/error.html', {'message': 'İşlem oluşturulamadı. Lütfen tekrar deneyin.'}, status=500)
    ctx = {
        'price': price,
        'ref': ref,
        'bank_holder': getattr(settings, 'BANK_ACCOUNT_HOLDER', ''),
        'bank_iban': getattr(settings, 'BANK_ACCOUNT_IBAN', ''),
        'bank_name': getattr(settings, 'BANK_ACCOUNT_BANK', ''),
    }
    return render(request, 'billing/bank_transfer.html', ctx)

@login_required
def portal(request: HttpRequest) -> HttpResponse:
    profile, _ = SubscriptionProfile.objects.get_or_create(user=request.user)
    trx = Transaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    bank = BankTransfer.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'billing/portal.html', {'profile': profile, 'transactions': trx, 'bank_transfers': bank})

@staff_member_required(login_url='/accounts/login/')
def admin_confirm_bank_transfer(request: HttpRequest, reference_code: str) -> HttpResponse:
    bt = BankTransfer.objects.get(reference_code=reference_code, is_confirmed=False)
    bt.confirm()
    _activate_subscription(bt.user, bt.plan, bt.price)
    # Create invoice after bank confirmation
    _create_invoice_for_subscription(None, bank_transfer=bt)
    return redirect('billing:portal')

def _activate_subscription(user, plan, price):
    profile, _ = SubscriptionProfile.objects.get_or_create(user=user)
    previous_plan = profile.plan
    profile.plan = plan
    profile.status = 'active'
    # Periyoda göre dönem 
    if price.period == 'month':
        profile.current_period_end = timezone.now() + timezone.timedelta(days=30)
    else:
        profile.current_period_end = timezone.now() + timezone.timedelta(days=365)
    profile.save()

    # Eski Accounts abonelik tipi ile uyumlu loglama (opsiyonel köprü)
    # Varsa aynı isimli SubscriptionType'a eşle
    try:
        stype = SubscriptionType.objects.filter(code__iexact=plan.code).first()
        if stype:
            acc_sub, _ = Subscription.objects.get_or_create(user=user, defaults={'subscription_type': stype})
            old_type = acc_sub.subscription_type
            acc_sub.subscription_type = stype
            acc_sub.save(update_fields=['subscription_type'])
            SubscriptionLog.objects.create(user=user, old_subscription=old_type, new_subscription=stype, note='Billing activation')
    except Exception:
        pass

    # Plan → Group atama
    try:
        if previous_plan and getattr(previous_plan, 'id', None) != getattr(plan, 'id', None):
            old_groups = PlanGroup.objects.filter(plan=previous_plan).values_list('group_id', flat=True)
            if old_groups:
                user.groups.remove(*Group.objects.filter(id__in=old_groups))
        new_groups = PlanGroup.objects.filter(plan=plan).values_list('group_id', flat=True)
        if new_groups:
            user.groups.add(*Group.objects.filter(id__in=new_groups))
    except Exception:
        pass

def _create_invoice_for_subscription(trx=None, bank_transfer=None):
    try:
        source = trx or bank_transfer
        if not source:
            return
        user = getattr(source, 'user', None)
        plan = getattr(source, 'plan', None)
        price = getattr(source, 'price', None)
        if not (user and plan and price):
            return
        company = getattr(user, 'company', None)
        if not company:
            return
        # Customer yoksa kullanıcıya müşteri oluştur
        cust, _ = Customer.objects.get_or_create(company=company, email=user.email or '', defaults={
            'first_name': user.first_name or user.username,
            'last_name': user.last_name or '',
        })
        period_label = 'Aylık' if getattr(price, 'period', 'month') == 'month' else 'Yıllık'
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
