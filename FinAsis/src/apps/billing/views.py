from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from .models import Plan, Price, SubscriptionProfile, Transaction, BankTransfer
from .services import PayTRClient, RefGenerator
from decimal import Decimal
from django.utils import timezone
from src.apps.accounts.models import SubscriptionType, Subscription, SubscriptionLog
from django.contrib.auth.models import Group
from .models import PlanGroup
from src.apps.accounting.models import Invoice, Customer, Company

@login_required
def plans(request: HttpRequest) -> HttpResponse:
    plans = Plan.objects.filter(is_active=True).prefetch_related('prices')
    return render(request, 'billing/plans.html', {
        'plans': plans,
        'BANK_TRANSFER_ENABLED': getattr(settings, 'BANK_TRANSFER_ENABLED', True),
    })

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
        'merchant_id': settings.PAYTR_MERCHANT_ID,
        'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
        'merchant_oid': f"OID{getattr(user, 'id', 0)}{int(timezone.now().timestamp())}",
        'email': user_email,
        'payment_amount': amount_kurus,
        'user_basket_b64': basket,
        'no_installment': 0,
        'max_installment': 12,
        'currency': 'TL',
        'test_mode': 1 if settings.PAYTR_SANDBOX else 0,
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
    ref = RefGenerator.bank_reference()
    BankTransfer.objects.create(
        user=request.user, plan=price.plan, price=price, amount=price.amount, currency=price.currency, reference_code=ref
    )
    ctx = {
        'price': price,
        'ref': ref,
        'bank_holder': settings.BANK_ACCOUNT_HOLDER,
        'bank_iban': settings.BANK_ACCOUNT_IBAN,
        'bank_name': settings.BANK_ACCOUNT_BANK,
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
