from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from .models import (
    ChartOfAccounts, Account, Invoice, InvoiceLine,
    Transaction, TransactionLine, CashBox, Bank, Stock, StockTransaction, EDocument, EDocumentSettings,
    Tax, Currency, ExchangeRate, Budget, BudgetCategory, DailyTask,
    UserDailyTask, KnowledgeBase, UserKnowledgeRead, TaskCategory, TaskCompletion, TaskNote
)
from .forms import (
    AccountForm, InvoiceForm, InvoiceLineForm, InvoiceLineFormSet,
    TransactionForm, TransactionLineForm, TransactionLineFormSet,
    BankForm, StockForm, StockTransactionForm, ChartOfAccountsForm, CashBoxForm,
    EDocumentCreateForm, EDocumentFilterForm, EDocumentCancelForm, EDocumentSettingsForm,
    DailyTaskForm, TaskResourceFormSet
)
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, FileResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
from .services import EDocumentService
from django.template.loader import render_to_string
from django.db import transaction
import os
import mimetypes
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator

@login_required
def dashboard(request):
    """Muhasebe modülü ana sayfası"""
    virtual_company = request.user.virtual_company
    context = {
        'total_invoices': Invoice.objects.filter(virtual_company=virtual_company).count(),
        'total_transactions': Transaction.objects.filter(virtual_company=virtual_company).count(),
        'total_banks': Bank.objects.filter(virtual_company=virtual_company).count(),
        'total_stocks': Stock.objects.filter(virtual_company=virtual_company).count(),
    }
    return render(request, 'accounting/dashboard.html', context)

# Hesap Planı Views
@login_required
def chart_of_accounts(request):
    accounts = ChartOfAccounts.objects.filter(
        virtual_company=request.user.virtual_company
    ).order_by('code')
    return render(request, 'accounting/chart_of_accounts.html', {'accounts': accounts})

@login_required
def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.virtual_company = request.user.virtual_company
            account.save()
            messages.success(request, 'Hesap başarıyla eklendi.')
            return redirect('accounting:chart_of_accounts')
    else:
        form = AccountForm()
    return render(request, 'accounting/account_form.html', {'form': form})

@login_required
def edit_account(request, pk):
    account = get_object_or_404(Account, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hesap başarıyla güncellendi.')
            return redirect('accounting:chart_of_accounts')
    else:
        form = AccountForm(instance=account)
    return render(request, 'accounting/account_form.html', {'form': form})

@login_required
def delete_account(request, pk):
    account = get_object_or_404(Account, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Hesap başarıyla silindi.')
        return redirect('accounting:chart_of_accounts')
    return render(request, 'accounting/account_confirm_delete.html', {'account': account})

# Cari Hesap Views
@login_required
def account_list(request):
    accounts = Account.objects.filter(virtual_company=request.user.virtual_company)
    return render(request, 'accounting/account_list.html', {'accounts': accounts})

@login_required
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk, virtual_company=request.user.virtual_company)
    return render(request, 'accounting/account_detail.html', {'account': account})

@login_required
def account_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.virtual_company = request.user.virtual_company
            account.save()
            messages.success(request, 'Cari hesap başarıyla oluşturuldu.')
            return redirect('accounting:account_list')
    else:
        form = AccountForm()
    return render(request, 'accounting/account_form.html', {'form': form})

@login_required
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cari hesap başarıyla güncellendi.')
            return redirect('accounting:account_list')
    else:
        form = AccountForm(instance=account)
    return render(request, 'accounting/account_form.html', {'form': form})

@login_required
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Cari hesap başarıyla silindi.')
        return redirect('accounting:account_list')
    return render(request, 'accounting/account_confirm_delete.html', {'account': account})

# Fatura Views
@login_required
def invoice_list(request):
    invoices = Invoice.objects.filter(virtual_company=request.user.virtual_company)
    return render(request, 'accounting/invoice_list.html', {'invoices': invoices})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, virtual_company=request.user.virtual_company)
    return render(request, 'accounting/invoice_detail.html', {'invoice': invoice})

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.virtual_company = request.user.virtual_company
            invoice.save()
            
            lines = formset.save(commit=False)
            for line in lines:
                line.invoice = invoice
                line.save()
            
            messages.success(request, 'Fatura başarıyla oluşturuldu.')
            return redirect('accounting:invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceLineFormSet()
    
    return render(request, 'accounting/invoice_form.html', {
        'form': form,
        'formset': formset
    })

@login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceLineFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Fatura başarıyla güncellendi.')
            return redirect('accounting:invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceLineFormSet(instance=invoice)
    
    return render(request, 'accounting/invoice_form.html', {
        'form': form,
        'formset': formset
    })

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Fatura başarıyla silindi.')
        return redirect('accounting:invoice_list')
    return render(request, 'accounting/invoice_confirm_delete.html', {'invoice': invoice})

# İşlem Views
@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(virtual_company=request.user.virtual_company)
    return render(request, 'accounting/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, virtual_company=request.user.virtual_company)
    return render(request, 'accounting/transaction_detail.html', {'transaction': transaction})

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        formset = TransactionLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            transaction = form.save(commit=False)
            transaction.virtual_company = request.user.virtual_company
            transaction.save()
            
            lines = formset.save(commit=False)
            for line in lines:
                line.transaction = transaction
                line.save()
            
            messages.success(request, 'İşlem başarıyla oluşturuldu.')
            return redirect('accounting:transaction_list')
    else:
        form = TransactionForm()
        formset = TransactionLineFormSet()
    
    return render(request, 'accounting/transaction_form.html', {
        'form': form,
        'formset': formset
    })

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        formset = TransactionLineFormSet(request.POST, instance=transaction)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'İşlem başarıyla güncellendi.')
            return redirect('accounting:transaction_list')
    else:
        form = TransactionForm(instance=transaction)
        formset = TransactionLineFormSet(instance=transaction)
    
    return render(request, 'accounting/transaction_form.html', {
        'form': form,
        'formset': formset
    })

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'İşlem başarıyla silindi.')
        return redirect('accounting:transaction_list')
    return render(request, 'accounting/transaction_confirm_delete.html', {'transaction': transaction})

# Kasa Views
@login_required
def cash_box_list(request):
    cash_boxes = CashBox.objects.filter(virtual_company=request.user.virtual_company)
    return render(request, 'accounting/cash_box_list.html', {'cash_boxes': cash_boxes})

@login_required
def cash_box_detail(request, pk):
    cash_box = get_object_or_404(CashBox, pk=pk, virtual_company=request.user.virtual_company)
    return render(request, 'accounting/cash_box_detail.html', {'cash_box': cash_box})

@login_required
def cash_box_create(request):
    if request.method == 'POST':
        form = CashBoxForm(request.POST)
        if form.is_valid():
            cash_box = form.save(commit=False)
            cash_box.virtual_company = request.user.virtual_company
            cash_box.save()
            messages.success(request, 'Kasa başarıyla oluşturuldu.')
            return redirect('accounting:cash_box_list')
    else:
        form = CashBoxForm()
    return render(request, 'accounting/cash_box_form.html', {'form': form})

@login_required
def cash_box_edit(request, pk):
    cash_box = get_object_or_404(CashBox, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        form = CashBoxForm(request.POST, instance=cash_box)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kasa başarıyla güncellendi.')
            return redirect('accounting:cash_box_list')
    else:
        form = CashBoxForm(instance=cash_box)
    return render(request, 'accounting/cash_box_form.html', {'form': form})

@login_required
def cash_box_delete(request, pk):
    cash_box = get_object_or_404(CashBox, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        cash_box.delete()
        messages.success(request, 'Kasa başarıyla silindi.')
        return redirect('accounting:cash_box_list')
    return render(request, 'accounting/cash_box_confirm_delete.html', {'cash_box': cash_box})

# Banka Views
@login_required
def bank_list(request):
    banks = Bank.objects.filter(virtual_company=request.user.virtual_company)
    return render(request, 'accounting/bank_list.html', {'banks': banks})

@login_required
def bank_detail(request, pk):
    bank = get_object_or_404(Bank, pk=pk, virtual_company=request.user.virtual_company)
    return render(request, 'accounting/bank_detail.html', {'bank': bank})

@login_required
def bank_create(request):
    if request.method == 'POST':
        form = BankForm(request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            bank.virtual_company = request.user.virtual_company
            bank.save()
            messages.success(request, 'Banka hesabı başarıyla oluşturuldu.')
            return redirect('accounting:bank_list')
    else:
        form = BankForm()
    return render(request, 'accounting/bank_form.html', {'form': form})

@login_required
def bank_edit(request, pk):
    bank = get_object_or_404(Bank, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banka hesabı başarıyla güncellendi.')
            return redirect('accounting:bank_list')
    else:
        form = BankForm(instance=bank)
    return render(request, 'accounting/bank_form.html', {'form': form})

@login_required
def bank_delete(request, pk):
    bank = get_object_or_404(Bank, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        bank.delete()
        messages.success(request, 'Banka hesabı başarıyla silindi.')
        return redirect('accounting:bank_list')
    return render(request, 'accounting/bank_confirm_delete.html', {'bank': bank})

# Stok Views
@login_required
def stock_list(request):
    stocks = Stock.objects.filter(virtual_company=request.user.virtual_company)
    return render(request, 'accounting/stock_list.html', {'stocks': stocks})

@login_required
def stock_detail(request, pk):
    stock = get_object_or_404(Stock, pk=pk, virtual_company=request.user.virtual_company)
    return render(request, 'accounting/stock_detail.html', {'stock': stock})

@login_required
def stock_create(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.virtual_company = request.user.virtual_company
            stock.save()
            messages.success(request, 'Stok başarıyla oluşturuldu.')
            return redirect('accounting:stock_list')
    else:
        form = StockForm()
    return render(request, 'accounting/stock_form.html', {'form': form})

@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stok başarıyla güncellendi.')
            return redirect('accounting:stock_list')
    else:
        form = StockForm(instance=stock)
    return render(request, 'accounting/stock_form.html', {'form': form})

@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk, virtual_company=request.user.virtual_company)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, 'Stok başarıyla silindi.')
        return redirect('accounting:stock_list')
    return render(request, 'accounting/stock_confirm_delete.html', {'stock': stock})

# Stok Hareketi Views
@login_required
def stock_transaction_list(request):
    transactions = StockTransaction.objects.filter(virtual_company=request.user.virtual_company)
    return render(request, 'accounting/stock_transaction_list.html', {'transactions': transactions})

@login_required
def stock_transaction_detail(request, pk):
    transaction = get_object_or_404(StockTransaction, pk=pk, virtual_company=request.user.virtual_company)
    return render(request, 'accounting/stock_transaction_detail.html', {'transaction': transaction})

@login_required
def stock_transaction_add(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.virtual_company = request.user.virtual_company
            
            # Stok miktarını güncelle
            stock = transaction.stock
            if transaction.type == 'income':
                stock.quantity += transaction.quantity
            else:
                if stock.quantity < transaction.quantity:
                    messages.error(request, 'Stok miktarı yetersiz!')
                    return render(request, 'accounting/stock_transaction_add.html', {'form': form})
                stock.quantity -= transaction.quantity
            
            stock.save()
            transaction.save()
            messages.success(request, 'Stok hareketi başarıyla eklendi.')
            return redirect('accounting:stock_transaction_list')
    else:
        form = StockTransactionForm()
    
    stocks = Stock.objects.filter(virtual_company=request.user.virtual_company, is_active=True)
    return render(request, 'accounting/stock_transaction_add.html', {
        'form': form,
        'stocks': stocks
    })

@login_required
def stock_transaction_edit(request, pk):
    transaction = get_object_or_404(StockTransaction, pk=pk, virtual_company=request.user.virtual_company)
    
    if request.method == 'POST':
        form = StockTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            # Eski stok miktarını geri al
            old_stock = transaction.stock
            if transaction.type == 'income':
                old_stock.quantity -= transaction.quantity
            else:
                old_stock.quantity += transaction.quantity
            old_stock.save()
            
            # Yeni değerleri kaydet
            updated_transaction = form.save(commit=False)
            
            # Yeni stok miktarını güncelle
            new_stock = updated_transaction.stock
            if updated_transaction.type == 'income':
                new_stock.quantity += updated_transaction.quantity
            else:
                if new_stock.quantity < updated_transaction.quantity:
                    messages.error(request, 'Stok miktarı yetersiz!')
                    return render(request, 'accounting/stock_transaction_edit.html', {
                        'form': form,
                        'transaction': transaction,
                        'stocks': Stock.objects.filter(virtual_company=request.user.virtual_company, is_active=True)
                    })
                new_stock.quantity -= updated_transaction.quantity
            
            new_stock.save()
            updated_transaction.save()
            messages.success(request, 'Stok hareketi başarıyla güncellendi.')
            return redirect('accounting:stock_transaction_detail', pk=updated_transaction.pk)
    else:
        form = StockTransactionForm(instance=transaction)
    
    stocks = Stock.objects.filter(virtual_company=request.user.virtual_company, is_active=True)
    return render(request, 'accounting/stock_transaction_edit.html', {
        'form': form,
        'transaction': transaction,
        'stocks': stocks
    })

@login_required
def stock_transaction_delete(request, pk):
    transaction = get_object_or_404(StockTransaction, pk=pk, virtual_company=request.user.virtual_company)
    
    if request.method == 'POST':
        # Stok miktarını geri al
        stock = transaction.stock
        if transaction.type == 'income':
            stock.quantity -= transaction.quantity
        else:
            stock.quantity += transaction.quantity
        stock.save()
        
        transaction.delete()
        messages.success(request, 'Stok hareketi başarıyla silindi.')
        return redirect('accounting:stock_transaction_list')
    
    return render(request, 'accounting/stock_transaction_delete.html', {'transaction': transaction})

# Hesap Planı Görünümleri
class ChartOfAccountsListView(LoginRequiredMixin, ListView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_list.html'
    context_object_name = 'accounts'
    ordering = ['code']

class ChartOfAccountsDetailView(LoginRequiredMixin, DetailView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_detail.html'
    context_object_name = 'account'

class ChartOfAccountsCreateView(LoginRequiredMixin, CreateView):
    model = ChartOfAccounts
    form_class = ChartOfAccountsForm
    template_name = 'accounting/chart_of_accounts_form.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')

    def form_valid(self, form):
        messages.success(self.request, 'Hesap planı başarıyla oluşturuldu.')
        return super().form_valid(form)

class ChartOfAccountsUpdateView(LoginRequiredMixin, UpdateView):
    model = ChartOfAccounts
    form_class = ChartOfAccountsForm
    template_name = 'accounting/chart_of_accounts_form.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')

    def form_valid(self, form):
        messages.success(self.request, 'Hesap planı başarıyla güncellendi.')
        return super().form_valid(form)

class ChartOfAccountsDeleteView(LoginRequiredMixin, DeleteView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_confirm_delete.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Hesap planı başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Cari Hesap Görünümleri
class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'accounting/account_list.html'
    context_object_name = 'accounts'
    ordering = ['code']

class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'accounting/account_detail.html'
    context_object_name = 'account'

class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounting/account_form.html'
    success_url = reverse_lazy('accounting:account_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cari hesap başarıyla oluşturuldu.')
        return super().form_valid(form)

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounting/account_form.html'
    success_url = reverse_lazy('accounting:account_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cari hesap başarıyla güncellendi.')
        return super().form_valid(form)

class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    template_name = 'accounting/account_confirm_delete.html'
    success_url = reverse_lazy('accounting:account_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Cari hesap başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Fatura Görünümleri
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'accounting/invoice_list.html'
    context_object_name = 'invoices'
    ordering = ['-date']

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'accounting/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.get_object()
        
        # Fatura kalemlerini context'e ekle
        context['invoice_lines'] = invoice.lines.all()
        
        # E-belge kontrollerini ekle
        context['has_edocument'] = invoice.edocument_set.exists()
        context['can_create_edocument'] = invoice.can_create_e_invoice and not invoice.edocument_set.exists()
        
        # Eğer faturanın e-belgesi varsa, detayları context'e ekle
        if context['has_edocument']:
            context['edocument'] = invoice.edocument_set.first()
        
        return context

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'accounting/invoice_form.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fatura başarıyla oluşturuldu.')
        return super().form_valid(form)

class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'accounting/invoice_form.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fatura başarıyla güncellendi.')
        return super().form_valid(form)

class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'accounting/invoice_confirm_delete.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Fatura başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Fatura Kalemi Görünümleri
class InvoiceLineCreateView(LoginRequiredMixin, CreateView):
    model = InvoiceLine
    form_class = InvoiceLineForm
    template_name = 'accounting/invoice_line_form.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fatura kalemi başarıyla oluşturuldu.')
        return super().form_valid(form)

class InvoiceLineUpdateView(LoginRequiredMixin, UpdateView):
    model = InvoiceLine
    form_class = InvoiceLineForm
    template_name = 'accounting/invoice_line_form.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fatura kalemi başarıyla güncellendi.')
        return super().form_valid(form)

class InvoiceLineDeleteView(LoginRequiredMixin, DeleteView):
    model = InvoiceLine
    template_name = 'accounting/invoice_line_confirm_delete.html'
    success_url = reverse_lazy('accounting:invoice_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Fatura kalemi başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Yevmiye Görünümleri
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'accounting/transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-date']

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'accounting/transaction_detail.html'
    context_object_name = 'transaction'

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'accounting/transaction_form.html'
    success_url = reverse_lazy('accounting:transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Yevmiye başarıyla oluşturuldu.')
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'accounting/transaction_form.html'
    success_url = reverse_lazy('accounting:transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Yevmiye başarıyla güncellendi.')
        return super().form_valid(form)

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'accounting/transaction_confirm_delete.html'
    success_url = reverse_lazy('accounting:transaction_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Yevmiye başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Yevmiye Kalemi Görünümleri
class TransactionLineCreateView(LoginRequiredMixin, CreateView):
    model = TransactionLine
    form_class = TransactionLineForm
    template_name = 'accounting/transaction_line_form.html'
    success_url = reverse_lazy('accounting:transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Yevmiye kalemi başarıyla oluşturuldu.')
        return super().form_valid(form)

class TransactionLineUpdateView(LoginRequiredMixin, UpdateView):
    model = TransactionLine
    form_class = TransactionLineForm
    template_name = 'accounting/transaction_line_form.html'
    success_url = reverse_lazy('accounting:transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Yevmiye kalemi başarıyla güncellendi.')
        return super().form_valid(form)

class TransactionLineDeleteView(LoginRequiredMixin, DeleteView):
    model = TransactionLine
    template_name = 'accounting/transaction_line_confirm_delete.html'
    success_url = reverse_lazy('accounting:transaction_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Yevmiye kalemi başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Kasa Görünümleri
class CashBoxListView(LoginRequiredMixin, ListView):
    model = CashBox
    template_name = 'accounting/cashbox_list.html'
    context_object_name = 'cashboxes'
    ordering = ['code']

class CashBoxDetailView(LoginRequiredMixin, DetailView):
    model = CashBox
    template_name = 'accounting/cashbox_detail.html'
    context_object_name = 'cashbox'

class CashBoxCreateView(LoginRequiredMixin, CreateView):
    model = CashBox
    form_class = CashBoxForm
    template_name = 'accounting/cashbox_form.html'
    success_url = reverse_lazy('accounting:cashbox_list')

    def form_valid(self, form):
        messages.success(self.request, 'Kasa başarıyla oluşturuldu.')
        return super().form_valid(form)

class CashBoxUpdateView(LoginRequiredMixin, UpdateView):
    model = CashBox
    form_class = CashBoxForm
    template_name = 'accounting/cashbox_form.html'
    success_url = reverse_lazy('accounting:cashbox_list')

    def form_valid(self, form):
        messages.success(self.request, 'Kasa başarıyla güncellendi.')
        return super().form_valid(form)

class CashBoxDeleteView(LoginRequiredMixin, DeleteView):
    model = CashBox
    template_name = 'accounting/cashbox_confirm_delete.html'
    success_url = reverse_lazy('accounting:cashbox_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Kasa başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Banka Görünümleri
class BankListView(LoginRequiredMixin, ListView):
    model = Bank
    template_name = 'accounting/bank_list.html'
    context_object_name = 'banks'
    ordering = ['code']

class BankDetailView(LoginRequiredMixin, DetailView):
    model = Bank
    template_name = 'accounting/bank_detail.html'
    context_object_name = 'bank'

class BankCreateView(LoginRequiredMixin, CreateView):
    model = Bank
    form_class = BankForm
    template_name = 'accounting/bank_form.html'
    success_url = reverse_lazy('accounting:bank_list')

    def form_valid(self, form):
        messages.success(self.request, 'Banka başarıyla oluşturuldu.')
        return super().form_valid(form)

class BankUpdateView(LoginRequiredMixin, UpdateView):
    model = Bank
    form_class = BankForm
    template_name = 'accounting/bank_form.html'
    success_url = reverse_lazy('accounting:bank_list')

    def form_valid(self, form):
        messages.success(self.request, 'Banka başarıyla güncellendi.')
        return super().form_valid(form)

class BankDeleteView(LoginRequiredMixin, DeleteView):
    model = Bank
    template_name = 'accounting/bank_confirm_delete.html'
    success_url = reverse_lazy('accounting:bank_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Banka başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Stok Görünümleri
class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'accounting/stock_list.html'
    context_object_name = 'stocks'
    ordering = ['code']

class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'accounting/stock_detail.html'
    context_object_name = 'stock'

class StockCreateView(LoginRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'accounting/stock_form.html'
    success_url = reverse_lazy('accounting:stock_list')

    def form_valid(self, form):
        messages.success(self.request, 'Stok başarıyla oluşturuldu.')
        return super().form_valid(form)

class StockUpdateView(LoginRequiredMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'accounting/stock_form.html'
    success_url = reverse_lazy('accounting:stock_list')

    def form_valid(self, form):
        messages.success(self.request, 'Stok başarıyla güncellendi.')
        return super().form_valid(form)

class StockDeleteView(LoginRequiredMixin, DeleteView):
    model = Stock
    template_name = 'accounting/stock_confirm_delete.html'
    success_url = reverse_lazy('accounting:stock_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Stok başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# Stok Hareketi Görünümleri
class StockTransactionListView(LoginRequiredMixin, ListView):
    model = StockTransaction
    template_name = 'accounting/stock_transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-date']

class StockTransactionDetailView(LoginRequiredMixin, DetailView):
    model = StockTransaction
    template_name = 'accounting/stock_transaction_detail.html'
    context_object_name = 'transaction'

class StockTransactionCreateView(LoginRequiredMixin, CreateView):
    model = StockTransaction
    form_class = StockTransactionForm
    template_name = 'accounting/stock_transaction_form.html'
    success_url = reverse_lazy('accounting:stock_transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Stok hareketi başarıyla oluşturuldu.')
        return super().form_valid(form)

class StockTransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = StockTransaction
    form_class = StockTransactionForm
    template_name = 'accounting/stock_transaction_form.html'
    success_url = reverse_lazy('accounting:stock_transaction_list')

    def form_valid(self, form):
        messages.success(self.request, 'Stok hareketi başarıyla güncellendi.')
        return super().form_valid(form)

class StockTransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = StockTransaction
    template_name = 'accounting/stock_transaction_confirm_delete.html'
    success_url = reverse_lazy('accounting:stock_transaction_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Stok hareketi başarıyla silindi.')
        return super().delete(request, *args, **kwargs)

# E-Belge görünümleri
@login_required
def e_document_list(request):
    """E-Belgeleri listeler"""
    # Filtreleme parametreleri
    document_type = request.GET.get('type')
    status = request.GET.get('status')
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    
    # Temel sorgu
    documents = EDocument.objects.all().order_by('-created_at')
    
    # Filtreleri uygula
    if document_type:
        documents = documents.filter(document_type=document_type)
    if status:
        documents = documents.filter(status=status)
    if date_start:
        documents = documents.filter(created_at__gte=date_start)
    if date_end:
        documents = documents.filter(created_at__lte=date_end)
    
    # Sayfalama
    paginator = Paginator(documents, 20)
    page = request.GET.get('page')
    documents = paginator.get_page(page)
    
    context = {
        'documents': documents,
        'document_types': EDocument.DOCUMENT_TYPES,
        'status_choices': EDocument.STATUS_CHOICES,
        'filters': {
            'type': document_type,
            'status': status,
            'date_start': date_start,
            'date_end': date_end
        }
    }
    
    return render(request, 'accounting/e_document_list.html', context)

@login_required
def e_document_detail(request, pk):
    """E-Belge detaylarını gösterir"""
    e_document = get_object_or_404(EDocument, pk=pk)
    
    # E-Belge durumunu kontrol et ve güncelle
    if e_document.status == 'PENDING':
        e_document_service = EDocumentService()
        try:
            status = e_document_service.check_document_status(e_document)
            if status != e_document.status:
                e_document.status = status
                e_document.save()
        except Exception as e:
            messages.warning(request, f'E-Belge durumu kontrol edilirken hata oluştu: {str(e)}')
    
    context = {
        'e_document': e_document,
        'invoice': e_document.invoice,
        'status_colors': {
            'DRAFT': 'secondary',
            'PENDING': 'warning',
            'APPROVED': 'success',
            'REJECTED': 'danger',
            'CANCELED': 'dark',
            'ERROR': 'danger'
        }
    }
    
    return render(request, 'accounting/e_document_detail.html', context)

@login_required
def create_e_invoice(request, invoice_id):
    """Faturadan e-fatura oluşturur"""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Faturayla ilişkili bir e-belge kontrolü
    if EDocument.objects.filter(invoice=invoice, document_type='INVOICE').exists():
        messages.error(request, f'{invoice.invoice_number} numaralı fatura için zaten bir e-fatura bulunmaktadır.')
        return redirect('accounting:invoice_detail', pk=invoice_id)
    
    try:
        # E-Fatura oluştur
        e_document_service = EDocumentService()
        e_document = e_document_service.create_e_invoice(invoice)
        
        # Başarılı mesajı göster
        messages.success(request, f'E-Fatura başarıyla oluşturuldu: {e_document.document_number}')
        
        # PDF dosyası varsa indirme linki ekle
        if e_document.pdf_file:
            messages.info(request, f'<a href="{e_document.pdf_file.url}" target="_blank">E-Fatura PDF</a> dosyasını indirebilirsiniz.', extra_tags='safe')
        
        return redirect('accounting:e_document_detail', pk=e_document.pk)
    except Exception as e:
        messages.error(request, f'E-Fatura oluşturma hatası: {str(e)}')
        return redirect('accounting:invoice_detail', pk=invoice_id)

@login_required
def create_e_archive_invoice(request, invoice_id):
    """Faturadan e-arşiv fatura oluşturur"""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Faturayla ilişkili bir e-arşiv fatura kontrolü
    if EDocument.objects.filter(invoice=invoice, document_type='ARCHIVE_INVOICE').exists():
        messages.error(request, f'{invoice.invoice_number} numaralı fatura için zaten bir e-arşiv fatura bulunmaktadır.')
        return redirect('accounting:invoice_detail', pk=invoice_id)
    
    try:
        # E-Arşiv Fatura oluştur
        e_document_service = EDocumentService()
        e_document = e_document_service.create_e_archive_invoice(invoice)
        
        # Başarılı mesajı göster
        messages.success(request, f'E-Arşiv Fatura başarıyla oluşturuldu: {e_document.document_number}')
        
        # PDF dosyası varsa indirme linki ekle
        if e_document.pdf_file:
            messages.info(request, f'<a href="{e_document.pdf_file.url}" target="_blank">E-Arşiv Fatura PDF</a> dosyasını indirebilirsiniz.', extra_tags='safe')
        
        return redirect('accounting:e_document_detail', pk=e_document.pk)
    except Exception as e:
        messages.error(request, f'E-Arşiv Fatura oluşturma hatası: {str(e)}')
        return redirect('accounting:invoice_detail', pk=invoice_id)

@login_required
def check_e_document_status(request, pk):
    """E-Belge durumunu günceller"""
    document = get_object_or_404(EDocument, pk=pk)
    
    try:
        e_document_service = EDocumentService()
        result = e_document_service.check_document_status(document)
        
        if result.get('success'):
            messages.success(request, f'E-Belge durumu güncellendi: {document.get_status_display()}')
        else:
            messages.error(request, f'E-Belge durumu güncellenirken hata oluştu: {result.get("error")}')
    except Exception as e:
        messages.error(request, f'E-Belge durumu sorgulama hatası: {str(e)}')
    
    return redirect('accounting:e_document_detail', pk=pk)

@login_required
def download_e_document_pdf(request, pk):
    """E-Belge PDF'ini indirir"""
    document = get_object_or_404(EDocument, pk=pk)
    
    # Eğer PDF zaten varsa doğrudan sunum
    if document.pdf_file:
        response = HttpResponse(document.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{document.document_number}.pdf"'
        return response
    
    # PDF yoksa indir
    try:
        e_document_service = EDocumentService()
        result = e_document_service.download_document_pdf(document)
        
        if result.get('success'):
            # Güncellenmiş belgeyi yeniden al
            document.refresh_from_db()
            response = HttpResponse(document.pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{document.document_number}.pdf"'
            return response
        else:
            messages.error(request, f'PDF indirme hatası: {result.get("error")}')
    except Exception as e:
        messages.error(request, f'PDF indirme hatası: {str(e)}')
    
    return redirect('accounting:e_document_detail', pk=pk)

@login_required
@require_POST
def cancel_e_document(request, pk):
    """E-Belgeyi iptal eder"""
    document = get_object_or_404(EDocument, pk=pk)
    
    # İptal edilebilir kontrolü
    if not document.can_be_canceled():
        messages.error(request, 'Bu belge iptal edilemez durumda.')
        return redirect('accounting:e_document_detail', pk=pk)
    
    reason = request.POST.get('cancel_reason')
    if not reason:
        messages.error(request, 'İptal gerekçesi belirtilmelidir.')
        return redirect('accounting:e_document_detail', pk=pk)
    
    try:
        e_document_service = EDocumentService()
        result = e_document_service.cancel_document(document, reason)
        
        if result.get('success'):
            messages.success(request, f'E-Belge başarıyla iptal edildi.')
        else:
            messages.error(request, f'E-Belge iptali sırasında hata oluştu: {result.get("error")}')
    except Exception as e:
        messages.error(request, f'E-Belge iptal hatası: {str(e)}')
    
    return redirect('accounting:e_document_detail', pk=pk)

# Fatura detay sayfasında e-belge bölümü için ajax fonksiyonu
@login_required
def invoice_e_documents(request, invoice_id):
    """Faturaya ait e-belgeleri getirir"""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    documents = EDocument.objects.filter(invoice=invoice).order_by('-created_at')
    
    html = render_to_string('accounting/includes/invoice_e_documents.html', {
        'documents': documents,
        'invoice': invoice,
    }, request=request)
    
    return JsonResponse({'html': html})

class EDocumentListView(LoginRequiredMixin, ListView):
    """E-belge listesi görünümü"""
    model = EDocument
    template_name = 'accounting/edocument_list.html'
    context_object_name = 'edocuments'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = EDocument.objects.all().order_by('-created_at')
        
        # Form ile gelen filtreler
        form = EDocumentFilterForm(self.request.GET)
        if form.is_valid():
            # Belge türü filtresi
            if form.cleaned_data.get('document_type'):
                queryset = queryset.filter(document_type=form.cleaned_data['document_type'])
            
            # Durum filtresi
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            # Tarih aralığı filtresi
            if form.cleaned_data.get('start_date'):
                queryset = queryset.filter(created_at__date__gte=form.cleaned_data['start_date'])
            if form.cleaned_data.get('end_date'):
                queryset = queryset.filter(created_at__date__lte=form.cleaned_data['end_date'])
            
            # Genel arama
            if form.cleaned_data.get('search'):
                search = form.cleaned_data['search']
                queryset = queryset.filter(
                    models.Q(document_number__icontains=search) |
                    models.Q(invoice__number__icontains=search) |
                    models.Q(invoice__account__name__icontains=search)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = EDocumentFilterForm(self.request.GET)
        return context


class EDocumentDetailView(LoginRequiredMixin, DetailView):
    """E-belge detay görünümü"""
    model = EDocument
    template_name = 'accounting/edocument_detail.html'
    context_object_name = 'edocument'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = self.object.invoice
        context['cancel_form'] = EDocumentCancelForm()
        return context


@login_required
def create_edocument(request, pk):
    """Faturadan e-belge oluşturma"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Eğer faturanın zaten bir e-belgesi varsa veya uygun değilse hata mesajı göster
    if invoice.edocument_set.exists():
        messages.error(request, _("Bu fatura için zaten bir e-belge oluşturulmuş."))
        return redirect('accounting:invoice_detail', pk=invoice.pk)
    
    if not invoice.can_create_e_invoice:
        messages.error(request, _("Bu fatura e-belge oluşturmak için uygun değil."))
        return redirect('accounting:invoice_detail', pk=invoice.pk)
    
    # Müşterinin e-fatura kullanıcısı olup olmadığını kontrol et
    is_e_invoice_user = False
    if hasattr(invoice.account, 'customer'):
        is_e_invoice_user = invoice.account.customer.is_e_invoice_user
    
    if request.method == 'POST':
        form = EDocumentCreateForm(request.POST, invoice=invoice, is_e_invoice_user=is_e_invoice_user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Yeni e-belge oluştur
                    edocument = EDocument.objects.create(
                        invoice=invoice,
                        document_type=form.cleaned_data['document_type'],
                        status='DRAFT',
                        notes=form.cleaned_data['notes'],
                        created_by=request.user
                    )
                    
                    # E-belge servisini çağır
                    service = EDocumentService()
                    
                    # Belge türüne göre işlem yap
                    if form.cleaned_data['document_type'] == 'EINVOICE':
                        result = service.create_e_invoice(edocument)
                    else:  # EARCHIVE
                        result = service.create_e_archive_invoice(edocument)
                    
                    if result:
                        messages.success(request, _("E-belge başarıyla oluşturuldu."))
                        return redirect('accounting:edocument_detail', pk=edocument.pk)
                    else:
                        messages.error(request, _("E-belge oluşturulurken bir hata oluştu."))
                        return redirect('accounting:invoice_detail', pk=invoice.pk)
            
            except Exception as e:
                messages.error(request, _("E-belge oluşturulurken bir hata oluştu: {}").format(str(e)))
                return redirect('accounting:invoice_detail', pk=invoice.pk)
    else:
        form = EDocumentCreateForm(invoice=invoice, is_e_invoice_user=is_e_invoice_user)
    
    return render(request, 'accounting/edocument_create.html', {
        'form': form,
        'invoice': invoice
    })


@login_required
def check_edocument_status(request, pk):
    """E-belge durumunu kontrol etme"""
    edocument = get_object_or_404(EDocument, pk=pk)
    
    # Belge zaten sonuçlanmış ise güncelleme yapma
    if edocument.is_finalized:
        messages.info(request, _("Belge zaten sonuçlanmış durumda, durum güncellemesi yapılmadı."))
        return redirect('accounting:edocument_detail', pk=edocument.pk)
    
    # E-belge servisi ile durum kontrolü yap
    service = EDocumentService()
    result = service.check_document_status(edocument)
    
    if result:
        if result.get('status_changed', False):
            messages.success(request, _("Belge durumu güncellendi: {}").format(edocument.get_status_display()))
        else:
            messages.info(request, _("Belge durumunda değişiklik yok: {}").format(edocument.get_status_display()))
    else:
        messages.error(request, _("Belge durumu kontrol edilirken bir hata oluştu."))
    
    return redirect('accounting:edocument_detail', pk=edocument.pk)


@login_required
def download_edocument(request, pk):
    """E-belge PDF dosyasını indirme"""
    edocument = get_object_or_404(EDocument, pk=pk)
    
    # Eğer PDF dosyası yoksa oluşturma işlemi yap
    if not edocument.pdf_file:
        service = EDocumentService()
        result = service.download_document_pdf(edocument)
        
        if not result:
            messages.error(request, _("PDF dosyası indirilemedi."))
            return redirect('accounting:edocument_detail', pk=edocument.pk)
    
    # PDF dosyası varsa indir
    try:
        file_path = edocument.pdf_file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                filename = edocument.get_pdf_filename()
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            messages.error(request, _("PDF dosyası bulunamadı."))
    except Exception as e:
        messages.error(request, _("PDF dosyası indirilirken bir hata oluştu: {}").format(str(e)))
    
    return redirect('accounting:edocument_detail', pk=edocument.pk)


@login_required
@require_POST
def cancel_edocument(request, pk):
    """E-belge iptali"""
    edocument = get_object_or_404(EDocument, pk=pk)
    
    # Belge iptal edilebilir durumda mı kontrol et
    if not edocument.can_be_canceled:
        messages.error(request, _("Bu belge iptal edilemez."))
        return redirect('accounting:edocument_detail', pk=edocument.pk)
    
    form = EDocumentCancelForm(request.POST)
    if form.is_valid():
        # E-belge servisi ile iptal et
        service = EDocumentService()
        result = service.cancel_document(edocument, form.cleaned_data['reason'])
        
        if result:
            messages.success(request, _("Belge başarıyla iptal edildi."))
        else:
            messages.error(request, _("Belge iptal edilirken bir hata oluştu."))
    else:
        messages.error(request, _("İptal işlemi için geçerli bir neden belirtmelisiniz."))
    
    return redirect('accounting:edocument_detail', pk=edocument.pk)

@login_required
def edocument_settings(request):
    """E-belge ayarları görünümü"""
    # Aktif ayarları al veya yeni bir tane oluştur
    try:
        settings = EDocumentSettings.objects.filter(is_active=True).first()
        if not settings:
            settings = EDocumentSettings.objects.first()
    except EDocumentSettings.DoesNotExist:
        settings = None
    
    if request.method == 'POST':
        # Mevcut ayarları güncelle veya yeni oluştur
        if settings:
            form = EDocumentSettingsForm(request.POST, instance=settings)
        else:
            form = EDocumentSettingsForm(request.POST)
        
        if form.is_valid():
            # Eğer bu ayar aktif olarak işaretlendiyse, diğerlerini devre dışı bırak
            if form.cleaned_data.get('is_active'):
                EDocumentSettings.objects.all().update(is_active=False)
            
            settings = form.save()
            messages.success(request, _("E-belge ayarları başarıyla kaydedildi."))
            return redirect('accounting:edocument_settings')
    else:
        # Form oluştur
        if settings:
            form = EDocumentSettingsForm(instance=settings)
        else:
            form = EDocumentSettingsForm()
    
    return render(request, 'accounting/edocument_settings.html', {
        'form': form,
        'settings': settings
    })

# Günlük Görevler View'ları
class DailyTaskListView(LoginRequiredMixin, ListView):
    model = DailyTask
    template_name = 'accounting/daily_tasks/task_list.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        # Aktif olan ve kullanıcının henüz tamamlamadığı görevleri getir
        completed_tasks = UserDailyTask.objects.filter(
            user=self.request.user, 
            completed=True
        ).values_list('task_id', flat=True)
        
        return DailyTask.objects.filter(
            active=True
        ).exclude(
            id__in=completed_tasks
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Kullanıcının tamamladığı görevleri de ekle
        context['completed_tasks'] = UserDailyTask.objects.filter(
            user=self.request.user,
            completed=True
        ).select_related('task')
        return context


class DailyTaskDetailView(LoginRequiredMixin, DetailView):
    model = DailyTask
    template_name = 'accounting/daily_tasks/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        
        # Görevin tamamlanma durumunu kontrol et
        user_task = UserDailyTask.objects.filter(
            user=self.request.user,
            task=task
        ).first()
        
        context['is_completed'] = user_task.completed if user_task else False
        
        # Görev için gerekli bilgi tabanı içeriklerini ekle
        context['knowledge_requirements'] = task.knowledge_required.all()
        
        # Kullanıcının okuduğu bilgi tabanı içeriklerini kontrol et
        if task.knowledge_required.exists():
            read_knowledge = UserKnowledgeRead.objects.filter(
                user=self.request.user,
                knowledge__in=task.knowledge_required.all()
            ).values_list('knowledge_id', flat=True)
            context['unread_knowledge'] = task.knowledge_required.exclude(id__in=read_knowledge)
        
        return context


class CompleteTaskView(LoginRequiredMixin, FormView):
    template_name = 'accounting/daily_tasks/complete_task.html'
    
    def get_success_url(self):
        return reverse('accounting:daily_task_list')
    
    def post(self, request, *args, **kwargs):
        task_id = self.kwargs.get('pk')
        try:
            task = DailyTask.objects.get(pk=task_id, active=True)
            
            # Görevin daha önce tamamlanıp tamamlanmadığını kontrol et
            user_task, created = UserDailyTask.objects.get_or_create(
                user=request.user,
                task=task,
                defaults={'completed': False}
            )
            
            if user_task.completed:
                messages.warning(request, _('Bu görevi zaten tamamladınız.'))
            else:
                # Görevin tamamlanma durumunu güncelle
                user_task.completed = True
                user_task.completed_at = timezone.now()
                user_task.save()
                
                # Kullanıcıya puan ekle
                user_profile = request.user.userprofile
                user_profile.total_points += task.points
                user_profile.save()
                
                messages.success(request, _('Tebrikler! Görevi başarıyla tamamladınız ve {} puan kazandınız.').format(task.points))
                
                # Eğer bilgi tabanı içerikleri okunmadıysa otomatik olarak okundu olarak işaretle
                for knowledge in task.knowledge_required.all():
                    UserKnowledgeRead.objects.get_or_create(
                        user=request.user,
                        knowledge=knowledge,
                        defaults={'read_at': timezone.now()}
                    )
            
            return redirect(self.get_success_url())
            
        except DailyTask.DoesNotExist:
            messages.error(request, _('Görev bulunamadı veya aktif değil.'))
            return redirect('accounting:daily_task_list')


# Bilgi Bankası View'ları
class KnowledgeBaseListView(LoginRequiredMixin, ListView):
    model = KnowledgeBase
    template_name = 'accounting/knowledge/knowledge_list.html'
    context_object_name = 'knowledge_items'
    
    def get_queryset(self):
        return KnowledgeBase.objects.filter(active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Kullanıcının okuduğu içerikleri işaretle
        read_knowledge = UserKnowledgeRead.objects.filter(
            user=self.request.user
        ).values_list('knowledge_id', flat=True)
        context['read_knowledge_ids'] = list(read_knowledge)
        return context


class KnowledgeBaseDetailView(LoginRequiredMixin, DetailView):
    model = KnowledgeBase
    template_name = 'accounting/knowledge/knowledge_detail.html'
    context_object_name = 'knowledge'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        knowledge = self.get_object()
        
        # Okundu olarak işaretle
        UserKnowledgeRead.objects.get_or_create(
            user=request.user,
            knowledge=knowledge,
            defaults={'read_at': timezone.now()}
        )
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        knowledge = self.get_object()
        
        # İlgili görevleri listele
        context['related_tasks'] = knowledge.related_tasks.filter(active=True)
        
        return context


# Kullanıcı istatistikleri
class UserStatsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/user_stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Günlük görev istatistikleri
        completed_tasks = UserDailyTask.objects.filter(user=user, completed=True)
        context['completed_tasks_count'] = completed_tasks.count()
        context['total_points'] = completed_tasks.aggregate(
            total=Sum('task__points'))['total'] or 0
        
        # Kategori bazında tamamlanan görevler
        category_stats = completed_tasks.values('task__category').annotate(
            count=Count('id'),
            points=Sum('task__points')
        ).order_by('-count')
        
        context['category_stats'] = category_stats
        
        # Zorluk seviyesine göre tamamlanan görevler
        difficulty_stats = completed_tasks.values('task__difficulty').annotate(
            count=Count('id'),
            points=Sum('task__points')
        ).order_by('task__difficulty')
        
        context['difficulty_stats'] = difficulty_stats
        
        # Okuma istatistikleri
        read_articles = UserKnowledgeRead.objects.filter(user=user)
        context['read_articles_count'] = read_articles.count()
        context['total_reads'] = read_articles.aggregate(
            total=Sum('read_count'))['total'] or 0
        
        # Kategori bazında okunan makaleler
        read_category_stats = read_articles.values('knowledge__category').annotate(
            count=Count('id'),
            reads=Sum('read_count')
        ).order_by('-reads')
        
        context['read_category_stats'] = read_category_stats
        
        return context

class DailyTaskCreateView(LoginRequiredMixin, CreateView):
    model = DailyTask
    template_name = 'accounting/daily_task_form.html'
    fields = ['title', 'description', 'category', 'difficulty', 'points', 'estimated_time', 'active', 'knowledge_required']
    success_url = reverse_lazy('accounting:daily_task_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Günlük görev başarıyla oluşturuldu!'))
        return super().form_valid(form)


class DailyTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = DailyTask
    template_name = 'accounting/daily_task_form.html'
    fields = ['title', 'description', 'category', 'difficulty', 'points', 'estimated_time', 'active', 'knowledge_required']
    success_url = reverse_lazy('accounting:daily_task_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Günlük görev başarıyla güncellendi!'))
        return super().form_valid(form)


class DailyTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = DailyTask
    template_name = 'accounting/daily_task_confirm_delete.html'
    success_url = reverse_lazy('accounting:daily_task_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Günlük görev başarıyla silindi!'))
        return super().delete(request, *args, **kwargs)


class KnowledgeBaseCreateView(LoginRequiredMixin, CreateView):
    model = KnowledgeBase
    template_name = 'accounting/knowledge_base_form.html'
    fields = ['title', 'content', 'summary', 'category', 'level', 'image', 'tags']
    success_url = reverse_lazy('accounting:knowledge_base_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Bilgi bankası makalesi başarıyla oluşturuldu!'))
        return super().form_valid(form)


class KnowledgeBaseUpdateView(LoginRequiredMixin, UpdateView):
    model = KnowledgeBase
    template_name = 'accounting/knowledge_base_form.html'
    fields = ['title', 'content', 'summary', 'category', 'level', 'image', 'tags']
    success_url = reverse_lazy('accounting:knowledge_base_list')
    
    def form_valid(self, form):
        messages.success(self.request, _('Bilgi bankası makalesi başarıyla güncellendi!'))
        return super().form_valid(form)


class KnowledgeBaseDeleteView(LoginRequiredMixin, DeleteView):
    model = KnowledgeBase
    template_name = 'accounting/knowledge_base_confirm_delete.html'
    success_url = reverse_lazy('accounting:knowledge_base_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _('Bilgi bankası makalesi başarıyla silindi!'))
        return super().delete(request, *args, **kwargs)
