# -*- coding: utf-8 -*-
"""
FinAsis Muhasebe Modülü - Görünümler

Bu modül, muhasebe modellerinin görünümlerini içerir.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Q
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import io
import pandas as pd
from reportlab.pdfgen import canvas
from django.utils import timezone

from .models import AccountType, Account, VoucherType, Voucher, VoucherLine
from .forms import (
    AccountTypeForm, AccountForm, VoucherTypeForm, VoucherForm, VoucherLineFormSet
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Muhasebe modülü ana sayfa görünümü"""
    template_name = 'accounting/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # İstatistikleri hesapla
        context['account_count'] = Account.objects.filter(company=self.request.user.company).count()
        context['active_account_count'] = Account.objects.filter(
            company=self.request.user.company, is_active=True
        ).count()
        
        context['voucher_count'] = Voucher.objects.filter(company=self.request.user.company).count()
        context['voucher_draft_count'] = Voucher.objects.filter(
            company=self.request.user.company, state='DRAFT'
        ).count()
        context['voucher_posted_count'] = Voucher.objects.filter(
            company=self.request.user.company, state='POSTED'
        ).count()
        
        # Son fişleri al
        context['recent_vouchers'] = Voucher.objects.filter(
            company=self.request.user.company
        ).order_by('-date', '-created_at')[:10]
        
        return context


# Hesap Türü görünümleri
class AccountTypeListView(LoginRequiredMixin, ListView):
    """Hesap türleri liste görünümü"""
    model = AccountType
    template_name = 'accounting/account_type_list.html'
    context_object_name = 'account_types'


class AccountTypeDetailView(LoginRequiredMixin, DetailView):
    """Hesap türü detay görünümü"""
    model = AccountType
    template_name = 'accounting/account_type_detail.html'
    context_object_name = 'account_type'


class AccountTypeCreateView(LoginRequiredMixin, CreateView):
    """Hesap türü oluşturma görünümü"""
    model = AccountType
    form_class = AccountTypeForm
    template_name = 'accounting/account_type_form.html'
    success_url = reverse_lazy('accounting:account_type_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Hesap türü başarıyla oluşturuldu."))
        return super().form_valid(form)


class AccountTypeUpdateView(LoginRequiredMixin, UpdateView):
    """Hesap türü güncelleme görünümü"""
    model = AccountType
    form_class = AccountTypeForm
    template_name = 'accounting/account_type_form.html'
    success_url = reverse_lazy('accounting:account_type_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Hesap türü başarıyla güncellendi."))
        return super().form_valid(form)


class AccountTypeDeleteView(LoginRequiredMixin, DeleteView):
    """Hesap türü silme görünümü"""
    model = AccountType
    template_name = 'accounting/account_type_confirm_delete.html'
    success_url = reverse_lazy('accounting:account_type_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Hesap türü başarıyla silindi."))
        return super().delete(request, *args, **kwargs)


# Hesap görünümleri
class AccountListView(LoginRequiredMixin, ListView):
    """Hesap liste görünümü"""
    model = Account
    template_name = 'accounting/account_list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        """Kullanıcının şirketine ait hesapları getir"""
        return Account.objects.filter(company=self.request.user.company).order_by('code')


class AccountDetailView(LoginRequiredMixin, DetailView):
    """Hesap detay görünümü"""
    model = Account
    template_name = 'accounting/account_detail.html'
    context_object_name = 'account'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Hesap hareketlerini al
        account = self.get_object()
        context['voucher_lines'] = VoucherLine.objects.filter(
            account=account, voucher__state='POSTED'
        ).order_by('-voucher__date', '-voucher__created_at')
        
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    """Hesap oluşturma görünümü"""
    model = Account
    form_class = AccountForm
    template_name = 'accounting/account_form.html'
    success_url = reverse_lazy('accounting:account_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs
    
    def form_valid(self, form):
        form.instance.company = self.request.user.company
        messages.success(self.request, _("Hesap başarıyla oluşturuldu."))
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """Hesap güncelleme görünümü"""
    model = Account
    form_class = AccountForm
    template_name = 'accounting/account_form.html'
    success_url = reverse_lazy('accounting:account_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, _("Hesap başarıyla güncellendi."))
        return super().form_valid(form)


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """Hesap silme görünümü"""
    model = Account
    template_name = 'accounting/account_confirm_delete.html'
    success_url = reverse_lazy('accounting:account_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Hesap başarıyla silindi."))
        return super().delete(request, *args, **kwargs)


# Fiş Türü görünümleri
class VoucherTypeListView(LoginRequiredMixin, ListView):
    """Fiş türleri liste görünümü"""
    model = VoucherType
    template_name = 'accounting/voucher_type_list.html'
    context_object_name = 'voucher_types'


class VoucherTypeDetailView(LoginRequiredMixin, DetailView):
    """Fiş türü detay görünümü"""
    model = VoucherType
    template_name = 'accounting/voucher_type_detail.html'
    context_object_name = 'voucher_type'


class VoucherTypeCreateView(LoginRequiredMixin, CreateView):
    """Fiş türü oluşturma görünümü"""
    model = VoucherType
    form_class = VoucherTypeForm
    template_name = 'accounting/voucher_type_form.html'
    success_url = reverse_lazy('accounting:voucher_type_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Fiş türü başarıyla oluşturuldu."))
        return super().form_valid(form)


class VoucherTypeUpdateView(LoginRequiredMixin, UpdateView):
    """Fiş türü güncelleme görünümü"""
    model = VoucherType
    form_class = VoucherTypeForm
    template_name = 'accounting/voucher_type_form.html'
    success_url = reverse_lazy('accounting:voucher_type_list')
    
    def form_valid(self, form):
        messages.success(self.request, _("Fiş türü başarıyla güncellendi."))
        return super().form_valid(form)


class VoucherTypeDeleteView(LoginRequiredMixin, DeleteView):
    """Fiş türü silme görünümü"""
    model = VoucherType
    template_name = 'accounting/voucher_type_confirm_delete.html'
    success_url = reverse_lazy('accounting:voucher_type_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Fiş türü başarıyla silindi."))
        return super().delete(request, *args, **kwargs)


# Fiş görünümleri
class VoucherListView(LoginRequiredMixin, ListView):
    """Fiş liste görünümü"""
    model = Voucher
    template_name = 'accounting/voucher_list.html'
    context_object_name = 'vouchers'
    
    def get_queryset(self):
        """Kullanıcının şirketine ait fişleri getir"""
        return Voucher.objects.filter(company=self.request.user.company).order_by('-date', '-created_at')


class VoucherDetailView(LoginRequiredMixin, DetailView):
    """Fiş detay görünümü"""
    model = Voucher
    template_name = 'accounting/voucher_detail.html'
    context_object_name = 'voucher'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voucher_lines'] = self.object.lines.all().order_by('line_no')
        return context


class VoucherCreateView(LoginRequiredMixin, CreateView):
    """Fiş oluşturma görünümü"""
    model = Voucher
    form_class = VoucherForm
    template_name = 'accounting/voucher_form.html'
    success_url = reverse_lazy('accounting:voucher_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = VoucherLineFormSet(self.request.POST)
        else:
            context['formset'] = VoucherLineFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            form.instance.company = self.request.user.company
            form.instance.created_by = self.request.user
            self.object = form.save()
            
            if formset.is_valid():
                formset.instance = self.object
                line_no = 1
                for form in formset:
                    if form.cleaned_data.get('account'):
                        form.instance.line_no = line_no
                        form.save()
                        line_no += 1
            
            messages.success(self.request, _("Muhasebe fişi başarıyla oluşturuldu."))
            return redirect(self.get_success_url())
        
        return self.form_invalid(form)


class VoucherUpdateView(LoginRequiredMixin, UpdateView):
    """Fiş güncelleme görünümü"""
    model = Voucher
    form_class = VoucherForm
    template_name = 'accounting/voucher_form.html'
    success_url = reverse_lazy('accounting:voucher_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = VoucherLineFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = VoucherLineFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        if self.object.state != 'DRAFT':
            messages.error(self.request, _("Sadece taslak durumdaki fişler düzenlenebilir."))
            return redirect('accounting:voucher_detail', pk=self.object.pk)
        
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                
                # Satır numaralarını yeniden sırala
                for i, line in enumerate(self.object.lines.all().order_by('line_no')):
                    line.line_no = i + 1
                    line.save()
            
            messages.success(self.request, _("Muhasebe fişi başarıyla güncellendi."))
            return redirect(self.get_success_url())
        
        return self.form_invalid(form)


class VoucherDeleteView(LoginRequiredMixin, DeleteView):
    """Fiş silme görünümü"""
    model = Voucher
    template_name = 'accounting/voucher_confirm_delete.html'
    success_url = reverse_lazy('accounting:voucher_list')
    
    def delete(self, request, *args, **kwargs):
        voucher = self.get_object()
        if voucher.state != 'DRAFT':
            messages.error(request, _("Sadece taslak durumdaki fişler silinebilir."))
            return redirect('accounting:voucher_detail', pk=voucher.pk)
        
        messages.success(request, _("Muhasebe fişi başarıyla silindi."))
        return super().delete(request, *args, **kwargs)


@login_required
def post_voucher(request, pk):
    """Fişi onaylama görünümü"""
    voucher = get_object_or_404(Voucher, pk=pk, company=request.user.company)
    
    if voucher.state != 'DRAFT':
        messages.error(request, _("Sadece taslak durumdaki fişler onaylanabilir."))
        return redirect('accounting:voucher_detail', pk=voucher.pk)
    
    try:
        voucher.post()
        messages.success(request, _("Muhasebe fişi başarıyla onaylandı."))
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('accounting:voucher_detail', pk=voucher.pk)


@login_required
def cancel_voucher(request, pk):
    """Fişi iptal etme görünümü"""
    voucher = get_object_or_404(Voucher, pk=pk, company=request.user.company)
    
    if voucher.state != 'DRAFT':
        messages.error(request, _("Sadece taslak durumdaki fişler iptal edilebilir. Onaylanmış fişler için ters kayıt oluşturun."))
        return redirect('accounting:voucher_detail', pk=voucher.pk)
    
    try:
        voucher.cancel()
        messages.success(request, _("Muhasebe fişi başarıyla iptal edildi."))
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('accounting:voucher_detail', pk=voucher.pk)


@login_required
def create_reverse_voucher(request, pk):
    """Ters kayıt oluşturma görünümü"""
    source_voucher = get_object_or_404(Voucher, pk=pk, company=request.user.company)
    
    if source_voucher.state != 'POSTED':
        messages.error(request, _("Sadece onaylanmış fişler için ters kayıt oluşturulabilir."))
        return redirect('accounting:voucher_detail', pk=source_voucher.pk)
    
    try:
        with transaction.atomic():
            # Ters fiş oluştur
            reverse_voucher = Voucher.objects.create(
                company=source_voucher.company,
                fiscal_year=source_voucher.fiscal_year,
                type=source_voucher.type,
                number=f"S-{source_voucher.number}",  # Storno prefix
                date=source_voucher.date,
                description=_("İPTAL: ") + source_voucher.description,
                reference=source_voucher.reference,
                created_by=request.user
            )
            
            # Ters fiş satırları oluştur
            for line in source_voucher.lines.all():
                VoucherLine.objects.create(
                    voucher=reverse_voucher,
                    line_no=line.line_no,
                    account=line.account,
                    description=_("İPTAL: ") + line.description,
                    debit_amount=line.credit_amount,  # Borç/alacak ters çevrilir
                    credit_amount=line.debit_amount   # Borç/alacak ters çevrilir
                )
            
            messages.success(request, _("Ters kayıt başarıyla oluşturuldu."))
            return redirect('accounting:voucher_detail', pk=reverse_voucher.pk)
            
    except Exception as e:
        messages.error(request, str(e))
        return redirect('accounting:voucher_detail', pk=source_voucher.pk)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_trial_balance(request):
    """
    Mizanı PDF veya Excel olarak dışa aktarır.
    ?format=pdf veya ?format=excel parametresi ile çıktı tipi seçilebilir.
    """
    format_ = request.GET.get('format', 'pdf')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not start_date or not end_date:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    
    # Hesap bakiyelerini topla
    accounts = Account.objects.all()
    data = []
    for acc in accounts:
        debit = VoucherLine.objects.filter(account=acc, voucher__date__gte=start_date, voucher__date__lte=end_date).aggregate(total=Sum('debit_amount'))['total'] or 0
        credit = VoucherLine.objects.filter(account=acc, voucher__date__gte=start_date, voucher__date__lte=end_date).aggregate(total=Sum('credit_amount'))['total'] or 0
        balance = debit - credit
        data.append({
            'Hesap Kodu': acc.code,
            'Hesap Adı': acc.name,
            'Borç': float(debit),
            'Alacak': float(credit),
            'Bakiye': float(balance),
        })
    
    if format_ == 'excel':
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Mizan')
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="mizan.xlsx"'
        return response
    else:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, "Mizan Raporu")
        y = 780
        for row in data:
            p.drawString(50, y, f"{row['Hesap Kodu']} - {row['Hesap Adı']} | Borç: {row['Borç']} | Alacak: {row['Alacak']} | Bakiye: {row['Bakiye']}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mizan.pdf"'
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_journal(request):
    """
    Yevmiye defterini PDF veya Excel olarak dışa aktarır.
    ?format=pdf veya ?format=excel parametresi ile çıktı tipi seçilebilir.
    """
    format_ = request.GET.get('format', 'pdf')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not start_date or not end_date:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    vouchers = Voucher.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date', 'number')
    data = []
    for v in vouchers:
        for line in v.lines.all():
            data.append({
                'Fiş No': v.number,
                'Tarih': v.date.strftime('%d.%m.%Y'),
                'Açıklama': v.description,
                'Hesap Kodu': line.account.code,
                'Hesap Adı': line.account.name,
                'Borç': float(line.debit_amount),
                'Alacak': float(line.credit_amount),
            })
    if format_ == 'excel':
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Yevmiye')
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="yevmiye.xlsx"'
        return response
    else:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, "Yevmiye Defteri")
        y = 780
        for row in data:
            p.drawString(50, y, f"{row['Fiş No']} | {row['Tarih']} | {row['Açıklama']} | {row['Hesap Kodu']} - {row['Hesap Adı']} | Borç: {row['Borç']} | Alacak: {row['Alacak']}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="yevmiye.pdf"'
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_general_ledger(request):
    """
    Defter-i kebiri PDF veya Excel olarak dışa aktarır.
    ?format=pdf veya ?format=excel parametresi ile çıktı tipi seçilebilir.
    """
    format_ = request.GET.get('format', 'pdf')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not start_date or not end_date:
        today = timezone.now().date()
        start_date = today.replace(day=1)
        end_date = today
    accounts = Account.objects.all()
    data = []
    for acc in accounts:
        lines = VoucherLine.objects.filter(account=acc, voucher__date__gte=start_date, voucher__date__lte=end_date).order_by('voucher__date', 'voucher__number')
        for line in lines:
            data.append({
                'Hesap Kodu': acc.code,
                'Hesap Adı': acc.name,
                'Fiş No': line.voucher.number,
                'Tarih': line.voucher.date.strftime('%d.%m.%Y'),
                'Açıklama': line.description,
                'Borç': float(line.debit_amount),
                'Alacak': float(line.credit_amount),
            })
    if format_ == 'excel':
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Defter-i Kebir')
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="defterikebir.xlsx"'
        return response
    else:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, "Defter-i Kebir")
        y = 780
        for row in data:
            p.drawString(50, y, f"{row['Hesap Kodu']} - {row['Hesap Adı']} | {row['Fiş No']} | {row['Tarih']} | {row['Açıklama']} | Borç: {row['Borç']} | Alacak: {row['Alacak']}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="defterikebir.pdf"'
        return response 