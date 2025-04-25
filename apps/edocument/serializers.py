from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    EDocument, EDocumentLog, EDocumentItem,
    EDespatchAdvice, EDespatchAdviceLog, EDespatchAdviceItem
)

class EDocumentItemSerializer(serializers.ModelSerializer):
    """E-Fatura kalemi serializer"""
    class Meta:
        model = EDocumentItem
        fields = [
            'id', 'line_number', 'product_code', 'product_name',
            'quantity', 'unit', 'unit_price', 'discount_rate',
            'discount_amount', 'tax_rate', 'tax_amount',
            'total_amount', 'notes'
        ]
        read_only_fields = ['id', 'total_amount']

    def validate(self, data):
        """Toplam tutar hesaplama ve doğrulama"""
        unit_price = data.get('unit_price', 0)
        quantity = data.get('quantity', 0)
        discount_rate = data.get('discount_rate', 0)
        tax_rate = data.get('tax_rate', 0)

        # İndirim tutarı hesaplama
        discount_amount = (unit_price * quantity * discount_rate) / 100
        data['discount_amount'] = discount_amount

        # Vergi tutarı hesaplama
        tax_amount = ((unit_price * quantity) - discount_amount) * (tax_rate / 100)
        data['tax_amount'] = tax_amount

        # Toplam tutar hesaplama
        total_amount = (unit_price * quantity) - discount_amount + tax_amount
        data['total_amount'] = total_amount

        return data

class EDocumentLogSerializer(serializers.ModelSerializer):
    """E-Fatura log serializer"""
    class Meta:
        model = EDocumentLog
        fields = [
            'id', 'action', 'status', 'level',
            'message', 'details', 'ip_address',
            'user_agent', 'created_at'
        ]
        read_only_fields = fields

class EDocumentSerializer(serializers.ModelSerializer):
    """E-Fatura serializer"""
    items = EDocumentItemSerializer(many=True, required=False)
    logs = EDocumentLogSerializer(many=True, read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(read_only=True)

    class Meta:
        model = EDocument
        fields = [
            'id', 'uuid', 'status', 'document_type',
            'invoice_number', 'invoice_date', 'due_date',
            'currency', 'exchange_rate', 'total_amount',
            'total_tax', 'total_discount', 'notes',
            'sender', 'sender_name', 'receiver_vkn',
            'receiver_name', 'xml_content', 'signed_xml',
            'signature_status', 'gib_response',
            'gib_error_message', 'created_at', 'updated_at',
            'sent_at', 'items', 'logs'
        ]
        read_only_fields = [
            'id', 'uuid', 'sender', 'sender_name',
            'xml_content', 'signed_xml', 'signature_status',
            'gib_response', 'gib_error_message', 'created_at',
            'updated_at', 'sent_at', 'logs'
        ]

    def validate(self, data):
        """Fatura doğrulama"""
        if data.get('due_date') and data.get('invoice_date'):
            if data['due_date'] < data['invoice_date']:
                raise serializers.ValidationError(
                    _('Vade tarihi fatura tarihinden önce olamaz')
                )
        
        # Toplam tutar hesaplama
        items = data.get('items', [])
        if items:
            total_amount = sum(item['total_amount'] for item in items)
            total_tax = sum(item['tax_amount'] for item in items)
            total_discount = sum(item['discount_amount'] for item in items)
            
            data['total_amount'] = total_amount
            data['total_tax'] = total_tax
            data['total_discount'] = total_discount
        
        return data

    def create(self, validated_data):
        """Fatura oluşturma"""
        items_data = validated_data.pop('items', [])
        document = EDocument.objects.create(**validated_data)
        
        for item_data in items_data:
            EDocumentItem.objects.create(document=document, **item_data)
        
        return document

    def update(self, instance, validated_data):
        """Fatura güncelleme"""
        items_data = validated_data.pop('items', [])
        
        # Fatura güncelleme
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Kalemleri güncelleme
        if items_data:
            # Mevcut kalemleri sil
            instance.items.all().delete()
            # Yeni kalemleri ekle
            for item_data in items_data:
                EDocumentItem.objects.create(document=instance, **item_data)
        
        return instance

class EDespatchAdviceItemSerializer(serializers.ModelSerializer):
    """E-İrsaliye kalemi serializer"""
    class Meta:
        model = EDespatchAdviceItem
        fields = [
            'id', 'line_number', 'product_code', 'product_name',
            'quantity', 'unit', 'accepted_quantity',
            'rejected_quantity', 'notes'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """Miktar doğrulama"""
        quantity = data.get('quantity', 0)
        accepted_quantity = data.get('accepted_quantity', 0)
        rejected_quantity = data.get('rejected_quantity', 0)

        if accepted_quantity + rejected_quantity > quantity:
            raise serializers.ValidationError(
                _('Kabul ve red miktarlarının toplamı, toplam miktardan büyük olamaz')
            )

        return data

class EDespatchAdviceLogSerializer(serializers.ModelSerializer):
    """E-İrsaliye log serializer"""
    class Meta:
        model = EDespatchAdviceLog
        fields = [
            'id', 'action', 'status', 'level',
            'message', 'details', 'ip_address',
            'user_agent', 'created_at'
        ]
        read_only_fields = fields

class EDespatchAdviceSerializer(serializers.ModelSerializer):
    """E-İrsaliye serializer"""
    items = EDespatchAdviceItemSerializer(many=True, required=False)
    logs = EDespatchAdviceLogSerializer(many=True, read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(read_only=True)

    class Meta:
        model = EDespatchAdvice
        fields = [
            'id', 'uuid', 'status', 'despatch_number',
            'despatch_date', 'delivery_date', 'transport_type',
            'vehicle_plate', 'driver_name', 'driver_tckn',
            'driver_phone', 'transport_company',
            'transport_company_vkn', 'notes', 'sender',
            'sender_name', 'receiver_vkn', 'receiver_name',
            'xml_content', 'signed_xml', 'signature_status',
            'gib_response', 'gib_error_message', 'created_at',
            'updated_at', 'sent_at', 'items', 'logs'
        ]
        read_only_fields = [
            'id', 'uuid', 'sender', 'sender_name',
            'xml_content', 'signed_xml', 'signature_status',
            'gib_response', 'gib_error_message', 'created_at',
            'updated_at', 'sent_at', 'logs'
        ]

    def validate(self, data):
        """İrsaliye doğrulama"""
        if data.get('delivery_date') and data.get('despatch_date'):
            if data['delivery_date'] < data['despatch_date']:
                raise serializers.ValidationError(
                    _('Teslimat tarihi irsaliye tarihinden önce olamaz')
                )
        
        # Taşıma tipine göre alan zorunluluğu
        transport_type = data.get('transport_type')
        if transport_type == 'COMPANY_VEHICLE':
            if not data.get('vehicle_plate'):
                raise serializers.ValidationError(
                    _('Firma aracı için plaka bilgisi zorunludur')
                )
        elif transport_type == 'TRANSPORTER':
            if not data.get('transport_company'):
                raise serializers.ValidationError(
                    _('Nakliyeci için firma bilgisi zorunludur')
                )
        
        return data

    def create(self, validated_data):
        """İrsaliye oluşturma"""
        items_data = validated_data.pop('items', [])
        despatch = EDespatchAdvice.objects.create(**validated_data)
        
        for item_data in items_data:
            EDespatchAdviceItem.objects.create(despatch=despatch, **item_data)
        
        return despatch

    def update(self, instance, validated_data):
        """İrsaliye güncelleme"""
        items_data = validated_data.pop('items', [])
        
        # İrsaliye güncelleme
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Kalemleri güncelleme
        if items_data:
            # Mevcut kalemleri sil
            instance.items.all().delete()
            # Yeni kalemleri ekle
            for item_data in items_data:
                EDespatchAdviceItem.objects.create(despatch=instance, **item_data)
        
        return instance 