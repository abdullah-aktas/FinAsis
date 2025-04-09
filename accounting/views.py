from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F
from django.utils import timezone
from .models import (
    ChartOfAccounts, Account, Invoice, InvoiceLine,
    Transaction, TransactionLine, CashBox, Bank, Stock, StockTransaction
)
from .forms import (
    AccountForm, InvoiceForm, InvoiceLineForm, InvoiceLineFormSet,
    TransactionForm, TransactionLineForm, TransactionLineFormSet,
    BankForm, StockForm, StockTransactionForm, ChartOfAccountsForm, CashBoxForm
)
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

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
