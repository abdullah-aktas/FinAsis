# -*- coding: utf-8 -*-
from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from .models import (
    Account, Invoice, InvoiceLine,
    Transaction, TransactionLine, Bank, Stock, StockTransaction, ChartOfAccounts, CashBox, EDocument, EDocumentSettings, DailyTask, KnowledgeBase, KnowledgeBaseRelatedItem
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

class EDocumentCreateForm(forms.Form):
    """E-belge oluşturma formu"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('EINVOICE', _('E-Fatura')),
        ('EARCHIVE', _('E-Arşiv Fatura')),
    ]
    
    document_type = forms.ChoiceField(
        label=_('Belge Türü'),
        choices=DOCUMENT_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial='EINVOICE'
    )
    
    notes = forms.CharField(
        label=_('Notlar'),
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        is_e_invoice_user = kwargs.pop('is_e_invoice_user', False)
        super().__init__(*args, **kwargs)
        
        # Eğer müşteri e-fatura mükellefi ise, e-arşiv seçeneğini kaldır
        if is_e_invoice_user:
            self.fields['document_type'].choices = [
                ('EINVOICE', _('E-Fatura'))
            ]
            self.fields['document_type'].initial = 'EINVOICE'
            self.fields['document_type'].widget = forms.HiddenInput()
        # Eğer müşteri e-fatura mükellefi değilse, sadece e-arşiv seçeneğini göster
        else:
            self.fields['document_type'].choices = [
                ('EARCHIVE', _('E-Arşiv Fatura'))
            ]
            self.fields['document_type'].initial = 'EARCHIVE'
            self.fields['document_type'].widget = forms.HiddenInput()

class EDocumentFilterForm(forms.Form):
    """E-belge listeleme filtre formu"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('', _('Tümü')),
        ('EINVOICE', _('E-Fatura')),
        ('EARCHIVE', _('E-Arşiv Fatura')),
        ('EDESPATCH', _('E-İrsaliye')),
        ('ERECEIPT', _('E-SMM')),
    ]
    
    STATUS_CHOICES = [
        ('', _('Tümü')),
        ('DRAFT', _('Taslak')),
        ('PENDING', _('İşleniyor')),
        ('APPROVED', _('Onaylandı')),
        ('REJECTED', _('Reddedildi')),
        ('CANCELED', _('İptal Edildi')),
        ('ERROR', _('Hata')),
    ]
    
    document_type = forms.ChoiceField(
        label=_('Belge Türü'),
        choices=DOCUMENT_TYPE_CHOICES,
        required=False
    )
    
    status = forms.ChoiceField(
        label=_('Durum'),
        choices=STATUS_CHOICES,
        required=False
    )
    
    start_date = forms.DateField(
        label=_('Başlangıç Tarihi'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    end_date = forms.DateField(
        label=_('Bitiş Tarihi'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    search = forms.CharField(
        label=_('Ara'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Belge no, müşteri adı...')})
    )

class EDocumentCancelForm(forms.Form):
    """E-belge iptal formu"""
    
    reason = forms.CharField(
        label=_('İptal Nedeni'),
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=_('İptal işlemi için geçerli bir neden belirtmelisiniz.'),
        required=True
    )

class EDocumentSettingsForm(forms.ModelForm):
    """E-belge ayarları için form"""
    
    class Meta:
        model = EDocumentSettings
        fields = [
            'company_name', 'vkn_tckn', 'tax_office', 'address', 'phone', 'email',
            'integration_type', 'api_url', 'api_key', 'username', 'password',
            'is_test_mode', 'is_active'
        ]
        widgets = {
            'password': forms.PasswordInput(render_value=True),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DailyTaskForm(forms.ModelForm):
    """Günlük görev formu"""
    
    class Meta:
        model = DailyTask
        fields = [
            'title', 'description', 'task_type', 'priority', 'status',
            'due_date', 'assigned_to', 'invoice', 'e_document',
            'reminder_date'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'reminder_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DailyTaskFilterForm(forms.Form):
    """Günlük görev filtreleme formu"""
    
    TYPE_CHOICES = [('', _('Tümü'))] + list(DailyTask.TASK_TYPE_CHOICES)
    STATUS_CHOICES = [('', _('Tümü'))] + list(DailyTask.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', _('Tümü'))] + list(DailyTask.PRIORITY_CHOICES)
    
    task_type = forms.ChoiceField(
        label=_('Görev Tipi'),
        choices=TYPE_CHOICES,
        required=False
    )
    
    status = forms.ChoiceField(
        label=_('Durum'),
        choices=STATUS_CHOICES,
        required=False
    )
    
    priority = forms.ChoiceField(
        label=_('Öncelik'),
        choices=PRIORITY_CHOICES,
        required=False
    )
    
    assigned_to = forms.ModelChoiceField(
        label=_('Atanan Kişi'),
        queryset=None,
        required=False
    )
    
    start_date = forms.DateField(
        label=_('Başlangıç Tarihi'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    end_date = forms.DateField(
        label=_('Bitiş Tarihi'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    search = forms.CharField(
        label=_('Ara'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Başlık, açıklama...')})
    )
    
    def __init__(self, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        # "Tümü" seçeneği ekle
        self.fields['assigned_to'].choices = [(None, _('Tümü'))] + list(self.fields['assigned_to'].choices)

class KnowledgeBaseForm(forms.ModelForm):
    """Bilgi bankası formu"""
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'title', 'content', 'category', 'tags', 'is_featured'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'rich-editor'}),
            'tags': forms.TextInput(attrs={'placeholder': _('Etiketleri virgülle ayırın')}),
        }

class KnowledgeBaseFilterForm(forms.Form):
    """Bilgi bankası filtreleme formu"""
    
    CATEGORY_CHOICES = [('', _('Tümü'))] + list(KnowledgeBase.CATEGORY_CHOICES)
    
    category = forms.ChoiceField(
        label=_('Kategori'),
        choices=CATEGORY_CHOICES,
        required=False
    )
    
    featured = forms.ChoiceField(
        label=_('Öne Çıkan'),
        choices=(
            ('', _('Tümü')),
            ('1', _('Öne Çıkanlar')),
            ('0', _('Standart')),
        ),
        required=False
    )
    
    tag = forms.CharField(
        label=_('Etiket'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Etiket ara...')})
    )
    
    search = forms.CharField(
        label=_('Ara'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Başlık, içerik...')})
    )

class TaskResourceForm(forms.ModelForm):
    """Görev kaynağı formu"""
    class Meta:
        model = KnowledgeBaseRelatedItem
        fields = ['title', 'description', 'url', 'resource_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
        }

TaskResourceFormSet = inlineformset_factory(
    DailyTask,
    KnowledgeBaseRelatedItem,
    form=TaskResourceForm,
    extra=1,
    can_delete=True
) 