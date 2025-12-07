"""
Finans ile ilgili formlar burada tanımlanır.
"""

from django import forms
from .models import (
    Transaction,
    Account,
    Budget,
    Tax,
    CashFlow,
    IncomeStatement,
    BankAccount,
    FinancialReport,
    EInvoice,
    EInvoiceItem,
    Employee,
    Voucher,
)
from .models import Invoice as MainInvoice

# class FinanceForm(forms.Form):
#     """Finans formu açıklaması."""
#     amount = forms.DecimalField(max_digits=10, decimal_places=2)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["type", "amount", "description", "transaction_date"]


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["name", "code", "type", "balance", "currency", "description"]


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = "__all__"


class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = "__all__"


class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = "__all__"


class IncomeStatementForm(forms.ModelForm):
    class Meta:
        model = IncomeStatement
        fields = "__all__"


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = "__all__"


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = MainInvoice
        fields = "__all__"


class FinancialReportForm(forms.ModelForm):
    class Meta:
        model = FinancialReport
        fields = "__all__"


class EInvoiceForm(forms.ModelForm):
    class Meta:
        model = EInvoice
        fields = "__all__"


class EInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = EInvoiceItem
        fields = "__all__"


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = "__all__"


class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = "__all__"
