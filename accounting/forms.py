from django import forms
from django.forms import inlineformset_factory
from .models import (
    Account, Invoice, InvoiceLine,
    Transaction, TransactionLine, Bank, Stock, StockTransaction, ChartOfAccounts, CashBox
)

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name', 'type', 'tax_number', 'address', 'phone', 'email']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['number', 'date', 'due_date', 'account', 'type', 'description']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'account': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = ['product', 'quantity', 'unit_price', 'tax_rate']
        widgets = {
            'product': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }

InvoiceLineFormSet = inlineformset_factory(
    Invoice, InvoiceLine,
    form=InvoiceLineForm,
    extra=1,
    can_delete=True
)

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'number', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TransactionLineForm(forms.ModelForm):
    class Meta:
        model = TransactionLine
        fields = ['account_code', 'description', 'debit', 'credit']
        widgets = {
            'account_code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control'}),
        }

TransactionLineFormSet = inlineformset_factory(
    Transaction, TransactionLine,
    form=TransactionLineForm,
    extra=1,
    can_delete=True
)

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['name', 'code', 'account_number', 'iban', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'iban': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['code', 'name', 'unit', 'quantity', 'unit_price']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['stock', 'date', 'type', 'quantity', 'description']
        widgets = {
            'stock': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ChartOfAccountsForm(forms.ModelForm):
    class Meta:
        model = ChartOfAccounts
        fields = ['code', 'name', 'type', 'parent']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

class CashBoxForm(forms.ModelForm):
    class Meta:
        model = CashBox
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 