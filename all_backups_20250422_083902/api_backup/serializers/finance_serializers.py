"""
Finans serileştiricileri
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from finance.models import EInvoice, EInvoiceItem, Customer, Product

class CustomerSerializer(serializers.ModelSerializer):
    """Müşteri serileştirici"""
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'tax_id', 'email', 'phone', 'address', 
                 'city', 'country', 'notes', 'created_by', 'created_at', 
                 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    """Ürün serileştirici"""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'barcode', 'price', 
                 'tax_rate', 'unit', 'stock_quantity', 'created_by', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

class EInvoiceItemSerializer(serializers.ModelSerializer):
    """E-Fatura öğesi serileştirici"""
    
    product_display = serializers.SerializerMethodField()
    
    class Meta:
        model = EInvoiceItem
        fields = ['id', 'product', 'product_display', 'description', 'quantity', 
                 'unit_price', 'tax_rate', 'tax_amount', 'total_amount']
        read_only_fields = ['id', 'tax_amount', 'total_amount']
    
    def get_product_display(self, obj):
        """Ürün adını döndür"""
        return obj.product.name if obj.product else None
    
    def validate(self, data):
        """E-Fatura öğesi verilerini doğrula"""
        quantity = data.get('quantity', 0)
        unit_price = data.get('unit_price', 0)
        
        if quantity <= 0:
            raise serializers.ValidationError(
                _("Miktar sıfırdan büyük olmalıdır.")
            )
        
        if unit_price <= 0:
            raise serializers.ValidationError(
                _("Birim fiyat sıfırdan büyük olmalıdır.")
            )
        
        return data

class EInvoiceSerializer(serializers.ModelSerializer):
    """E-Fatura serileştirici"""
    
    items = EInvoiceItemSerializer(many=True, read_only=True)
    customer_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = EInvoice
        fields = ['id', 'invoice_type', 'invoice_number', 'customer', 
                 'customer_display', 'issue_date', 'due_date', 'note', 
                 'status', 'status_display', 'items', 'subtotal', 'tax_total', 
                 'total_amount', 'created_by', 'updated_by', 'created_at', 
                 'updated_at', 'sent_date', 'paid_date']
        read_only_fields = ['id', 'invoice_number', 'subtotal', 'tax_total', 
                           'total_amount', 'created_by', 'updated_by', 
                           'created_at', 'updated_at', 'sent_date', 'paid_date']
    
    def get_customer_display(self, obj):
        """Müşteri adını döndür"""
        return obj.customer.name if obj.customer else None
    
    def get_status_display(self, obj):
        """Durum adını döndür"""
        return dict(EInvoice.STATUS_CHOICES).get(obj.status, "")
    
    def create(self, validated_data):
        """E-Fatura oluştur"""
        # Fatura numarası oluştur
        if not validated_data.get('invoice_number'):
            import uuid
            validated_data['invoice_number'] = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        # Durum ayarla
        if not validated_data.get('status'):
            validated_data['status'] = 'draft'
        
        return super().create(validated_data) 