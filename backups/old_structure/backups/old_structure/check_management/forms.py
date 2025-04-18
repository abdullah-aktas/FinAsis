from django import forms
from .models import Bank, Check, PromissoryNote, CheckTransaction, PromissoryNoteTransaction

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['name', 'code', 'branch_code', 'branch_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_code': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CheckForm(forms.ModelForm):
    class Meta:
        model = Check
        fields = [
            'check_number', 'bank', 'amount', 'issue_date', 'due_date',
            'status', 'check_type', 'drawer_name', 'drawer_tax_number',
            'payee_name', 'payee_tax_number', 'notes'
        ]
        widgets = {
            'check_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'check_type': forms.Select(attrs={'class': 'form-control'}),
            'drawer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'drawer_tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'payee_name': forms.TextInput(attrs={'class': 'form-control'}),
            'payee_tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class PromissoryNoteForm(forms.ModelForm):
    class Meta:
        model = PromissoryNote
        fields = [
            'note_number', 'amount', 'issue_date', 'due_date',
            'status', 'note_type', 'drawer_name', 'drawer_tax_number',
            'payee_name', 'payee_tax_number', 'notes'
        ]
        widgets = {
            'note_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'note_type': forms.Select(attrs={'class': 'form-control'}),
            'drawer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'drawer_tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'payee_name': forms.TextInput(attrs={'class': 'form-control'}),
            'payee_tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class CheckTransactionForm(forms.ModelForm):
    class Meta:
        model = CheckTransaction
        fields = [
            'transaction_type', 'transaction_date', 'amount',
            'reference_number', 'notes'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class PromissoryNoteTransactionForm(forms.ModelForm):
    class Meta:
        model = PromissoryNoteTransaction
        fields = [
            'transaction_type', 'transaction_date', 'amount',
            'reference_number', 'notes'
        ]
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'transaction_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        } 