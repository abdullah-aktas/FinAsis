from django import forms
from .models import Warehouse, Product, Stock, StockMovement, StockCount, StockCountItem

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'description', 'manager', 'status', 'capacity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Diğer formlar buraya eklenecek... 