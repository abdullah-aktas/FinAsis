# -*- coding: utf-8 -*-
"""
Enhanced Accounting Views
Django views for Turkish Standard Chart of Accounts and double-entry bookkeeping
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from decimal import Decimal
import json

from typing import TYPE_CHECKING, Any, Optional

# Açık model importları (wildcard kaldırıldı)
from finance.enhanced_accounting_models import (
    JournalVoucher,
    JournalEntry,
    ChartOfAccounts,
    FixedAsset,
    DepreciationEntry,
)
from accounting.models import Company

if TYPE_CHECKING:  # Statik analiz için user.company pseudo attribute
    from django.contrib.auth.models import AbstractUser as _UserBase
    class _UserWithCompany(_UserBase):  # pragma: no cover
        company: Company  # type: ignore[attr-defined]
    request_user_type = _UserWithCompany
else:  # runtime'da herhangi bir değişiklik yapmıyoruz
    request_user_type = Any  # pragma: no cover


class VoucherListView(LoginRequiredMixin, ListView):
    """
    Muhasebe fişleri listesi
    """
    model = JournalVoucher
    template_name = 'accounting/voucher_list.html'
    context_object_name = 'vouchers'
    paginate_by = 25
    
    def get_queryset(self):
        company = getattr(self.request.user, 'company', None)
        if not company:
            return JournalVoucher.objects.none()
        queryset = (
            JournalVoucher.objects.filter(company=company)
            .select_related('company')
            .prefetch_related('journal_entries')
            .order_by('-date', '-id')
        )
        
        # Filtreleme
        voucher_type = self.request.GET.get('type')
        if voucher_type:
            queryset = queryset.filter(voucher_type=voucher_type)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(voucher_number__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # İstatistikler
        company = getattr(self.request.user, 'company', None)
        if not company:
            context['stats'] = {
                'total_vouchers': 0,
                'this_month': 0,
                'total_amount': 0,
            }
            context['voucher_types'] = []
            return context
        context['stats'] = {
            'total_vouchers': JournalVoucher.objects.filter(company=company).count(),
            'this_month': JournalVoucher.objects.filter(
                company=company,
                date__year=timezone.now().year,
                date__month=timezone.now().month
            ).count(),
            'total_amount': JournalEntry.objects.filter(
                voucher__company=company
            ).aggregate(total=Sum('debit_amount'))['total'] or 0
        }
        
        # Fiş tipleri
        # VOUCHER_TYPES is defined on the model
        context['voucher_types'] = getattr(JournalVoucher, 'VOUCHER_TYPES', [])
        
        return context


class VoucherDetailView(LoginRequiredMixin, DetailView):
    """
    Muhasebe fişi detayı
    """
    model = JournalVoucher
    template_name = 'accounting/voucher_detail.html'
    context_object_name = 'voucher'
    
    def get_queryset(self):
        company = getattr(self.request.user, 'company', None)
        if not company:
            return JournalVoucher.objects.none()
        return (
            JournalVoucher.objects.filter(company=company)
            .select_related('company')
            .prefetch_related('journal_entries__account')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Toplam tutarları hesapla
        obj = getattr(self, 'object', None)
        entries = obj.journal_entries.all() if obj is not None else []
        context['total_debit'] = sum(entry.debit_amount for entry in entries)
        context['total_credit'] = sum(entry.credit_amount for entry in entries)
        context['is_balanced'] = context['total_debit'] == context['total_credit']
        
        return context


@login_required
def voucher_create(request):
    """
    Yeni muhasebe fişi oluşturma
    """
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('finance:kobi_dashboard')
    
    JournalEntryFormSet = modelformset_factory(
        JournalEntry,
        fields=('account', 'description', 'debit_amount', 'credit_amount'),
        extra=5,
        can_delete=True
    )
    
    if request.method == 'POST':
        voucher_form = JournalVoucherForm(request.POST)
        entry_formset = JournalEntryFormSet(request.POST, prefix='entries')
        
        if voucher_form.is_valid() and entry_formset.is_valid():
            try:
                with transaction.atomic():
                    # Fiş kaydet
                    voucher = voucher_form.save(commit=False)
                    voucher.company = company
                    
                    # Fiş numarası otomatik oluştur
                    if not voucher.voucher_number:
                        voucher.voucher_number = generate_voucher_number(company, voucher.voucher_type)
                    
                    voucher.save()
                    
                    # Kayıtları kaydet
                    total_debit = Decimal('0')
                    total_credit = Decimal('0')
                    entry_count = 0
                    
                    for entry_form in entry_formset:
                        if entry_form.cleaned_data and not entry_form.cleaned_data.get('DELETE', False):
                            entry = entry_form.save(commit=False)
                            entry.voucher = voucher
                            
                            # Boş tutar kontrolü
                            if not entry.debit_amount:
                                entry.debit_amount = Decimal('0')
                            if not entry.credit_amount:
                                entry.credit_amount = Decimal('0')
                            
                            # En az bir tarafta tutar olmalı
                            if entry.debit_amount > 0 or entry.credit_amount > 0:
                                entry.save()
                                total_debit += entry.debit_amount
                                total_credit += entry.credit_amount
                                entry_count += 1
                    
                    # Denge kontrolü
                    if abs(total_debit - total_credit) > Decimal('0.01'):
                        raise ValueError(_('Borç ve alacak tutarları eşit olmalıdır.'))
                    
                    if entry_count < 2:
                        raise ValueError(_('En az 2 kayıt girmelisiniz.'))
                    
                    # Taslak kontrolü
                    if request.POST.get('draft'):
                        voucher.is_draft = True
                        voucher.save()
                        messages.success(request, _('Fiş taslak olarak kaydedildi.'))
                        return JsonResponse({'success': True, 'message': str(_('Taslak kaydedildi'))})
                    
                    messages.success(request, _('Muhasebe fişi başarıyla kaydedildi.'))
                    return redirect('accounting:voucher_detail', pk=voucher.pk)
                    
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Kayıt sırasında hata oluştu: {str(e)}')
        else:
            messages.error(request, _('Form verilerinde hata var. Lütfen kontrol edin.'))
    else:
        voucher_form = JournalVoucherForm()
        entry_formset = JournalEntryFormSet(prefix='entries', queryset=JournalEntry.objects.none())
    
    # Hesap listesi
    accounts = ChartOfAccounts.objects.filter(company=company, is_active=True).order_by('code') if company else []
    
    context = {
        'form': voucher_form,
        'entry_formset': entry_formset,
        'accounts': accounts,
        'voucher_types': getattr(JournalVoucher, 'VOUCHER_TYPES', []),
    }
    
    return render(request, 'accounting/voucher_form.html', context)


@login_required
def voucher_edit(request, pk):
    """
    Muhasebe fişi düzenleme
    """
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('finance:kobi_dashboard')
    voucher = get_object_or_404(JournalVoucher, pk=pk, company=company)
    
    JournalEntryFormSet = modelformset_factory(
        JournalEntry,
        fields=('account', 'description', 'debit_amount', 'credit_amount'),
        extra=2,
        can_delete=True
    )
    
    if request.method == 'POST':
        voucher_form = JournalVoucherForm(request.POST, instance=voucher)
        entry_formset = JournalEntryFormSet(request.POST, prefix='entries')
        
        if voucher_form.is_valid() and entry_formset.is_valid():
            try:
                with transaction.atomic():
                    # Eski kayıtları sil
                    entries_rel = getattr(voucher, 'journal_entries', None)
                    if entries_rel is not None:
                        entries_rel.all().delete()
                    
                    # Fiş güncelle
                    voucher = voucher_form.save()
                    
                    # Yeni kayıtları kaydet
                    total_debit = Decimal('0')
                    total_credit = Decimal('0')
                    entry_count = 0
                    
                    for entry_form in entry_formset:
                        if entry_form.cleaned_data and not entry_form.cleaned_data.get('DELETE', False):
                            entry = entry_form.save(commit=False)
                            entry.voucher = voucher
                            
                            if not entry.debit_amount:
                                entry.debit_amount = Decimal('0')
                            if not entry.credit_amount:
                                entry.credit_amount = Decimal('0')
                            
                            if entry.debit_amount > 0 or entry.credit_amount > 0:
                                entry.save()
                                total_debit += entry.debit_amount
                                total_credit += entry.credit_amount
                                entry_count += 1
                    
                    # Denge kontrolü
                    if abs(total_debit - total_credit) > Decimal('0.01'):
                        raise ValueError(_('Borç ve alacak tutarları eşit olmalıdır.'))
                    
                    if entry_count < 2:
                        raise ValueError(_('En az 2 kayıt girmelisiniz.'))
                    
                    messages.success(request, _('Muhasebe fişi başarıyla güncellendi.'))
                    return redirect('accounting:voucher_detail', pk=voucher.pk)
                    
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Güncelleme sırasında hata oluştu: {str(e)}')
    else:
        voucher_form = JournalVoucherForm(instance=voucher)
        entries_rel = getattr(voucher, 'journal_entries', None)
        qs = entries_rel.all() if entries_rel is not None else JournalEntry.objects.none()
        entry_formset = JournalEntryFormSet(prefix='entries', queryset=qs)
    
    accounts = ChartOfAccounts.objects.filter(company=company, is_active=True).order_by('code') if company else []
    
    context = {
        'form': voucher_form,
        'entry_formset': entry_formset,
        'accounts': accounts,
        'object': voucher,
    }
    
    return render(request, 'accounting/voucher_form.html', context)


@login_required
def chart_of_accounts_view(request):
    """
    Hesap planı görüntüleme
    """
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('finance:kobi_dashboard')
    
    # Ana grup kodlarına göre hesapları grupla
    account_groups = {}
    accounts = ChartOfAccounts.objects.filter(company=company).order_by('code') if company else []
    
    for account in accounts:
        group_code = account.code[0]  # İlk rakam
        group_name = get_account_group_name(group_code)
        
        if group_name not in account_groups:
            account_groups[group_name] = []
        account_groups[group_name].append(account)
    
    # Her hesap için bakiye hesapla
    for group_accounts in account_groups.values():
        for account in group_accounts:
            account.balance = calculate_account_balance(account)
    
    context = {
        'account_groups': account_groups,
        'company': company,
    }
    
    return render(request, 'accounting/chart_of_accounts.html', context)


@login_required
def fixed_assets_view(request):
    """
    Sabit kıymetler listesi
    """
    company = getattr(request.user, 'company', None)
    if not company:
        messages.error(request, _('Şirket bilgisi bulunamadı.'))
        return redirect('finance:kobi_dashboard')
    assets = FixedAsset.objects.filter(company=company).order_by('-purchase_date')
    
    # Sayfalama
    paginator = Paginator(assets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Toplam değerler
    total_cost = assets.aggregate(total=Sum('cost'))['total'] or 0
    total_depreciation = DepreciationEntry.objects.filter(
        asset__company=company
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'page_obj': page_obj,
        'assets': page_obj,
        'total_cost': total_cost,
        'total_depreciation': total_depreciation,
        'net_value': total_cost - total_depreciation,
    }
    
    return render(request, 'accounting/fixed_assets.html', context)


@login_required
def ajax_search_accounts(request):
    """
    AJAX hesap arama
    """
    query = request.GET.get('q', '')
    company = getattr(request.user, 'company', None)
    if not company:
        return JsonResponse({'accounts': []})
    
    if len(query) < 2:
        return JsonResponse({'accounts': []})
    
    accounts = ChartOfAccounts.objects.filter(
        company=company,
        is_active=True
    ).filter(
        Q(code__icontains=query) | Q(name__icontains=query)
    ).order_by('code')[:20]
    
    account_list = []
    for account in accounts:
        account_list.append({
            'id': account.id,
            'code': account.code,
            'name': account.name,
            'account_type': getattr(account, 'get_account_type_display', lambda: '')(),
        })
    
    return JsonResponse({'accounts': account_list})


@login_required
def ajax_account_balance(request, account_id):
    """
    AJAX hesap bakiyesi
    """
    try:
        company = getattr(request.user, 'company', None)
        if not company:
            return JsonResponse({'success': False, 'error': 'Şirket bulunamadı'})
        account = ChartOfAccounts.objects.get(id=account_id, company=company)
        balance = calculate_account_balance(account)
        
        return JsonResponse({
            'success': True,
            'balance': float(balance),
            'formatted_balance': f"₺{balance:,.2f}".replace(',', '.').replace('.', ',', 1),
            'account_name': account.name,
        })
    except ChartOfAccounts.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Hesap bulunamadı'})


# Form sınıfları
from django import forms

class JournalVoucherForm(forms.ModelForm):
    """
    Muhasebe fişi formu
    """
    class Meta:
        model = JournalVoucher
        fields = ['voucher_number', 'date', 'voucher_type', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Otomatik oluşturulur'}),
            'voucher_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.now().date()
        self.fields['voucher_number'].required = False


class JournalEntryForm(forms.ModelForm):
    """
    Muhasebe kaydı formu
    """
    class Meta:
        model = JournalEntry
        fields = ['account', 'description', 'debit_amount', 'credit_amount']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select account-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'debit_amount': forms.NumberInput(attrs={
                'class': 'form-control amount-input',
                'step': '0.01',
                'min': '0'
            }),
            'credit_amount': forms.NumberInput(attrs={
                'class': 'form-control amount-input',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        debit = cleaned_data.get('debit_amount') or Decimal('0')
        credit = cleaned_data.get('credit_amount') or Decimal('0')
        
        # Aynı anda hem borç hem alacak girilemez
        if debit > 0 and credit > 0:
            raise forms.ValidationError(_('Aynı kayıtta hem borç hem alacak tutar girilemez.'))
        
        # En az birinde tutar olmalı
        if debit == 0 and credit == 0:
            raise forms.ValidationError(_('Borç veya alacak tutarlarından en az birini girmelisiniz.'))
        
        return cleaned_data


# Yardımcı fonksiyonlar
def generate_voucher_number(company, voucher_type):
    """
    Otomatik fiş numarası oluştur
    """
    today = timezone.now().date()
    year = today.year
    
    # Tip kısaltması
    type_prefix = {
        'GENERAL': 'MF',
        'SALE': 'SF',
        'PURCHASE': 'AF',
        'CASH': 'KF',
        'BANK': 'BF',
        'PAYROLL': 'PF',
        'DEPRECIATION': 'DF',
        'ADJUSTMENT': 'ADJ',
        'CLOSING': 'CL',
    }.get(voucher_type, 'MF')
    
    # Bu yıl için son numara
    last_voucher = JournalVoucher.objects.filter(
        company=company,
        voucher_type=voucher_type,
        date__year=year
    ).order_by('-voucher_number').first()
    
    if last_voucher and last_voucher.voucher_number:
        # Son numarayı çıkar
        try:
            last_number = int(last_voucher.voucher_number.split('-')[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1
    
    return f"{type_prefix}-{year}-{next_number:06d}"


def get_account_group_name(group_code):
    """
    Hesap grubu adını getir
    """
    group_names = {
        '1': _('Dönen Varlıklar'),
        '2': _('Duran Varlıklar'),
        '3': _('Kısa Vadeli Yabancı Kaynaklar'),
        '4': _('Uzun Vadeli Yabancı Kaynaklar'),
        '5': _('Öz Kaynaklar'),
        '6': _('Gelir Hesapları'),
        '7': _('Gider Hesapları'),
        '8': _('Serbest Hesaplar'),
        '9': _('Nazım Hesaplar'),
    }
    return group_names.get(group_code, _('Diğer'))


def calculate_account_balance(account):
    """
    Hesap bakiyesini hesapla
    """
    entries = JournalEntry.objects.filter(account=account)
    
    debit_total = entries.aggregate(total=Sum('debit_amount'))['total'] or Decimal('0')
    credit_total = entries.aggregate(total=Sum('credit_amount'))['total'] or Decimal('0')
    
    # Hesap tipine göre bakiye hesapla
    if account.account_type in ['ASSET', 'EXPENSE']:
        # Aktif ve gider hesapları: Borç - Alacak
        return debit_total - credit_total
    else:
        # Pasif, gelir ve sermaye hesapları: Alacak - Borç
        return credit_total - debit_total


@login_required
def account_ledger(request, account_id):
    """
    Hesap defteri görüntüleme
    """
    company = request.user.company
    account = get_object_or_404(ChartOfAccounts, id=account_id, company=company)
    
    # Filtreleme
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    entries = JournalEntry.objects.filter(account=account).select_related(
        'voucher'
    ).order_by('voucher__date', 'id')
    
    if date_from:
        entries = entries.filter(voucher__date__gte=date_from)
    if date_to:
        entries = entries.filter(voucher__date__lte=date_to)
    
    # Bakiye hesaplama
    running_balance = Decimal('0')
    entry_list = []
    
    for entry in entries:
        if account.account_type in ['ASSET', 'EXPENSE']:
            running_balance += entry.debit_amount - entry.credit_amount
        else:
            running_balance += entry.credit_amount - entry.debit_amount
        
        entry_list.append({
            'entry': entry,
            'running_balance': running_balance,
        })
    
    # Sayfalama
    paginator = Paginator(entry_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'account': account,
        'page_obj': page_obj,
        'final_balance': running_balance,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'accounting/account_ledger.html', context)


@login_required
def trial_balance(request):
    """
    Mizanı hesap görüntüleme
    """
    company = request.user.company
    
    # Tarih filtresi
    date_to = request.GET.get('date_to', timezone.now().date())
    
    accounts = ChartOfAccounts.objects.filter(
        company=company, is_active=True
    ).order_by('code')
    
    trial_balance_data = []
    total_debit = Decimal('0')
    total_credit = Decimal('0')
    
    for account in accounts:
        # Hesap hareketlerini getir
        entries = JournalEntry.objects.filter(
            account=account,
            voucher__date__lte=date_to
        )
        
        debit_sum = entries.aggregate(total=Sum('debit_amount'))['total'] or Decimal('0')
        credit_sum = entries.aggregate(total=Sum('credit_amount'))['total'] or Decimal('0')
        
        # Bakiye hesapla
        if account.account_type in ['ASSET', 'EXPENSE']:
            balance = debit_sum - credit_sum
            debit_balance = balance if balance > 0 else Decimal('0')
            credit_balance = -balance if balance < 0 else Decimal('0')
        else:
            balance = credit_sum - debit_sum
            credit_balance = balance if balance > 0 else Decimal('0')
            debit_balance = -balance if balance < 0 else Decimal('0')
        
        # Hareket yoksa atla
        if debit_sum == 0 and credit_sum == 0:
            continue
        
        trial_balance_data.append({
            'account': account,
            'debit_movements': debit_sum,
            'credit_movements': credit_sum,
            'debit_balance': debit_balance,
            'credit_balance': credit_balance,
        })
        
        total_debit += debit_balance
        total_credit += credit_balance
    
    context = {
        'trial_balance_data': trial_balance_data,
        'total_debit': total_debit,
        'total_credit': total_credit,
        'is_balanced': total_debit == total_credit,
        'date_to': date_to,
        'company': company,
    }
    
    return render(request, 'accounting/trial_balance.html', context)