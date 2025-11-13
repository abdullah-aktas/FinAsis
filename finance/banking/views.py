# -*- coding: utf-8 -*-
"""
Finance Banking Views
Banka Entegrasyonu ve Finansal İşlemler Görünümleri
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import timezone

from .models import (
    Bank,
    BankAccount,
    BankTransaction,
)


@login_required
def banking_dashboard(request):
    """
    Bankacılık ana dashboard
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    # Banka hesapları
    accounts = BankAccount.objects.filter(company=company)
    
    # Son işlemler (source veya destination'dan şirketin hesapları)
    recent_transactions = BankTransaction.objects.filter(
        company=company
    ).order_by('-transaction_date')[:20]
    
    # Toplam bakiyeler
    total_balance = sum(acc.current_balance if isinstance(acc.current_balance, (int, float)) else 0 for acc in accounts)
    
    # Bekleyen ödemeler (placeholder)
    pending_payments = []
    total_pending = 0
    
    context = {
        'company': company,
        'accounts': accounts,
        'total_accounts': accounts.count(),
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'pending_payments': pending_payments,
        'total_pending': total_pending,
    }
    
    return render(request, 'finance/banking/dashboard.html', context)


@login_required
def account_list(request):
    """
    Banka hesapları listesi
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    accounts = BankAccount.objects.filter(company=company)
    
    context = {
        'accounts': accounts,
    }
    
    return render(request, 'finance/banking/account_list.html', context)


@login_required
def transaction_list(request):
    """
    Banka işlemleri listesi
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    transactions = BankTransaction.objects.filter(
        company=company
    ).select_related('source_account', 'destination_account').order_by('-transaction_date')
    
    # Filtreleme
    account_filter = request.GET.get('account')
    if account_filter:
        from django.db.models import Q
        transactions = transactions.filter(
            Q(source_account_id=account_filter) | Q(destination_account_id=account_filter)
        )
    
    transaction_type_filter = request.GET.get('type')
    if transaction_type_filter:
        transactions = transactions.filter(transaction_type=transaction_type_filter)
    
    context = {
        'transactions': transactions,
        'accounts': BankAccount.objects.filter(company=company),
        'account_filter': account_filter,
        'transaction_type_filter': transaction_type_filter,
    }
    
    return render(request, 'finance/banking/transaction_list.html', context)


@login_required
def reconciliation_list(request):
    """
    Banka mutabakatları listesi
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    # Mutabakat bilgileri - transaction'lardan hesaplanacak
    reconciliations = []
    
    context = {
        'reconciliations': reconciliations,
    }
    
    return render(request, 'finance/banking/reconciliation_list.html', context)


@login_required
def payment_order_list(request):
    """
    Ödeme emirleri listesi
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        messages.warning(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('dashboard')
    
    # Ödeme emirleri - placeholder
    payment_orders = []
    status_filter = request.GET.get('status')
    
    context = {
        'payment_orders': payment_orders,
        'status_filter': status_filter,
    }
    
    return render(request, 'finance/banking/payment_order_list.html', context)


@login_required
def ajax_account_balance(request, account_id):
    """
    AJAX: Hesap bakiyesi sorgulama
    """
    try:
        company = getattr(request.user, 'company', None)
        account = BankAccount.objects.get(
            id=account_id,
            company=company
        )
        
        data = {
            'success': True,
            'account_number': account.account_number,
            'current_balance': float(account.current_balance),
            'available_balance': float(account.available_balance),
            'currency': account.currency,
            'last_updated': account.last_sync_date.isoformat() if account.last_sync_date else None,
        }
        
        return JsonResponse(data)
        
    except BankAccount.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Hesap bulunamadı')
        }, status=404)


@login_required
def ajax_sync_transactions(request, account_id):
    """
    AJAX: Banka işlemlerini senkronize et
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': _('Sadece POST istekleri kabul edilir')
        }, status=405)
    
    try:
        company = getattr(request.user, 'company', None)
        account = BankAccount.objects.get(
            id=account_id,
            company=company
        )
        
        # Burada gerçek banka API entegrasyonu yapılacak
        # Şimdilik sadece başarılı yanıt döndürüyoruz
        
        account.last_sync_date = timezone.now()
        account.save(update_fields=['last_sync_date'])
        
        return JsonResponse({
            'success': True,
            'message': _('İşlemler başarıyla senkronize edildi.'),
            'last_sync': account.last_sync_date.isoformat()
        })
        
    except BankAccount.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Hesap bulunamadı')
        }, status=404)


@login_required
def ajax_dashboard_stats(request):
    """
    AJAX: Dashboard istatistikleri
    """
    company = getattr(request.user, 'company', None)
    
    if not company:
        return JsonResponse({
            'success': False,
            'error': _('Şirket bilgisi bulunamadı')
        }, status=400)
    
    accounts = BankAccount.objects.filter(company=company)
    
    stats = {
        'total_accounts': accounts.count(),
        'total_balance': float(sum(acc.current_balance if isinstance(acc.current_balance, (int, float)) else 0 for acc in accounts)),
        'pending_payments': 0,  # Placeholder
        'recent_transaction_count': BankTransaction.objects.filter(
            company=company,
            transaction_date__gte=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })

