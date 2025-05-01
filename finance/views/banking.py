# -*- coding: utf-8 -*-
"""
Banka işlemleri ile ilgili görünümler
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Q

from finance.models import BankAccount, Transaction, TransactionCategory
from permissions.decorators import permission_required

class BankAccountListView(ListView):
    """Banka hesaplarını listeleyen görünüm"""
    model = BankAccount
    template_name = 'finance/bank_accounts.html'
    context_object_name = 'bank_accounts'
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = self.get_queryset()
        context['total_balance'] = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
        return context

class BankAccountDetailView(DetailView):
    """Banka hesabı detaylarını gösteren görünüm"""
    model = BankAccount
    template_name = 'finance/bank_account_detail.html'
    context_object_name = 'bank_account'
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bank_account = self.get_object()
        transactions = Transaction.objects.filter(
            Q(source_account=bank_account) | Q(destination_account=bank_account)
        ).order_by('-date')
        context['transactions'] = transactions[:10]  # Son 10 işlem
        return context

class BankAccountCreateView(CreateView):
    """Yeni banka hesabı oluşturma görünümü"""
    model = BankAccount
    template_name = 'finance/bank_account_form.html'
    fields = ['bank_name', 'account_number', 'iban', 'account_type', 'currency', 'balance', 'description']
    success_url = reverse_lazy('finance:bank_accounts')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Banka hesabı başarıyla oluşturuldu.'))
        return super().form_valid(form)

class BankAccountUpdateView(UpdateView):
    """Banka hesabı güncelleme görünümü"""
    model = BankAccount
    template_name = 'finance/bank_account_form.html'
    fields = ['bank_name', 'account_number', 'iban', 'account_type', 'currency', 'balance', 'description']
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('finance:bank_account_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('Banka hesabı başarıyla güncellendi.'))
        return super().form_valid(form)

class BankAccountDeleteView(DeleteView):
    """Banka hesabı silme görünümü"""
    model = BankAccount
    template_name = 'finance/bank_account_confirm_delete.html'
    success_url = reverse_lazy('finance:bank_accounts')
    
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Banka hesabı başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

class TransactionListView(ListView):
    """İşlemleri listeleyen görünüm"""
    model = Transaction
    template_name = 'finance/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(
            Q(source_account__user=self.request.user) | 
            Q(destination_account__user=self.request.user)
        ).order_by('-date')
        
        # Filtreleme
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
            
        account = self.request.GET.get('account')
        if account:
            queryset = queryset.filter(
                Q(source_account__id=account) | Q(destination_account__id=account)
            )
            
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = TransactionCategory.objects.all()
        context['accounts'] = BankAccount.objects.filter(user=self.request.user)
        return context

class TransactionDetailView(DetailView):
    """İşlem detaylarını gösteren görünüm"""
    model = Transaction
    template_name = 'finance/transaction_detail.html'
    context_object_name = 'transaction'
    
    def get_queryset(self):
        return Transaction.objects.filter(
            Q(source_account__user=self.request.user) | 
            Q(destination_account__user=self.request.user)
        )

class TransactionCreateView(CreateView):
    """Yeni işlem oluşturma görünümü"""
    model = Transaction
    template_name = 'finance/transaction_form.html'
    fields = ['transaction_type', 'amount', 'date', 'category', 'description', 
              'source_account', 'destination_account', 'reference_number']
    success_url = reverse_lazy('finance:transactions')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['source_account'].queryset = BankAccount.objects.filter(user=self.request.user)
        form.fields['destination_account'].queryset = BankAccount.objects.filter(user=self.request.user)
        return form
    
    def form_valid(self, form):
        messages.success(self.request, _('İşlem başarıyla kaydedildi.'))
        return super().form_valid(form)

class TransactionUpdateView(UpdateView):
    """İşlem güncelleme görünümü"""
    model = Transaction
    template_name = 'finance/transaction_form.html'
    fields = ['transaction_type', 'amount', 'date', 'category', 'description', 
              'source_account', 'destination_account', 'reference_number']
    
    def get_queryset(self):
        return Transaction.objects.filter(
            Q(source_account__user=self.request.user) | 
            Q(destination_account__user=self.request.user)
        )
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['source_account'].queryset = BankAccount.objects.filter(user=self.request.user)
        form.fields['destination_account'].queryset = BankAccount.objects.filter(user=self.request.user)
        return form
    
    def get_success_url(self):
        return reverse_lazy('finance:transaction_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _('İşlem başarıyla güncellendi.'))
        return super().form_valid(form)

class TransactionDeleteView(DeleteView):
    """İşlem silme görünümü"""
    model = Transaction
    template_name = 'finance/transaction_confirm_delete.html'
    success_url = reverse_lazy('finance:transactions')
    
    def get_queryset(self):
        return Transaction.objects.filter(
            Q(source_account__user=self.request.user) | 
            Q(destination_account__user=self.request.user)
        )
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('İşlem başarıyla silindi.'))
        return super().delete(request, *args, **kwargs)

# Function-based views
@login_required
@permission_required('finance.view_banksummary')
def bank_summary(request):
    """Banka hesapları özet görünümü"""
    accounts = BankAccount.objects.filter(user=request.user)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or 0
    
    # Son işlemler
    recent_transactions = Transaction.objects.filter(
        Q(source_account__user=request.user) | 
        Q(destination_account__user=request.user)
    ).order_by('-date')[:5]
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'finance/bank_summary.html', context) 