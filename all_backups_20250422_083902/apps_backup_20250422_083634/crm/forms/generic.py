from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Customer, Contact, Opportunity, Activity, Document, Sale

class CustomerForm(forms.ModelForm):
    """Müşteri formu"""
    class Meta:
        model = Customer
        fields = ['name', 'tax_number', 'tax_office', 'address', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Müşteri Adı'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vergi Numarası'}),
            'tax_office': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vergi Dairesi'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Adres', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta'}),
        }

class ContactForm(forms.ModelForm):
    """İletişim kişisi formu"""
    class Meta:
        model = Contact
        fields = ['customer', 'name', 'position', 'phone', 'email', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İletişim Kişisi Adı'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pozisyon'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notlar', 'rows': 3}),
        }

class OpportunityForm(forms.ModelForm):
    """Satış fırsatı formu"""
    class Meta:
        model = Opportunity
        fields = ['customer', 'name', 'value', 'probability', 'expected_close_date', 'status', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fırsat Adı'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tutar'}),
            'probability': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Olasılık (%)'}),
            'expected_close_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notlar', 'rows': 3}),
        }

class ActivityForm(forms.ModelForm):
    """Aktivite formu"""
    class Meta:
        model = Activity
        fields = ['customer', 'opportunity', 'type', 'subject', 'description', 'due_date', 'completed', 'assigned_to']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'opportunity': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Konu'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Açıklama', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

class DocumentForm(forms.ModelForm):
    """Belge formu"""
    class Meta:
        model = Document
        fields = ['customer', 'title', 'file', 'document_type', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Belge Adı'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Notlar', 'rows': 3}),
        }

class SaleForm(forms.ModelForm):
    """Satış formu"""
    class Meta:
        model = Sale
        fields = ['customer', 'date', 'description', 'payment_method', 'payment_date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Açıklama', 'rows': 3}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        } 