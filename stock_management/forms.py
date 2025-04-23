from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import Warehouse, Product, Stock, StockMovement, StockCount, StockCountItem, Category

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'description', 'manager', 'status', 'capacity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'barcode', 'category', 'description',
            'unit_price', 'tax_rate', 'min_stock_level', 'max_stock_level',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        min_stock = cleaned_data.get('min_stock_level')
        max_stock = cleaned_data.get('max_stock_level')

        if min_stock is not None and max_stock is not None:
            if min_stock > max_stock:
                raise forms.ValidationError(
                    _('Minimum stok seviyesi maksimum stok seviyesinden büyük olamaz.')
                )

        return cleaned_data

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'movement_type', 'quantity', 'reference', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'movement_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')

        if all([product, movement_type, quantity]):
            if movement_type == 'OUT' and quantity > product.current_stock:
                raise forms.ValidationError(
                    _('Yetersiz stok miktarı. Mevcut stok: %(current)s')
                    % {'current': product.current_stock}
                )

        return cleaned_data

class StockReportFilterForm(forms.Form):
    date_range = forms.ChoiceField(
        choices=[
            ('today', _('Bugün')),
            ('week', _('Bu Hafta')),
            ('month', _('Bu Ay')),
            ('year', _('Bu Yıl')),
            ('custom', _('Özel Tarih Aralığı')),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    stock_status = forms.ChoiceField(
        choices=[
            ('', _('Tümü')),
            ('low', _('Düşük Stok')),
            ('high', _('Yüksek Stok')),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        date_range = cleaned_data.get('date_range')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if date_range == 'custom':
            if not start_date or not end_date:
                raise forms.ValidationError(
                    _('Özel tarih aralığı seçildiğinde başlangıç ve bitiş tarihleri zorunludur.')
                )
            if start_date > end_date:
                raise forms.ValidationError(
                    _('Başlangıç tarihi bitiş tarihinden büyük olamaz.')
                )

        return cleaned_data

# Diğer formlar buraya eklenecek... 