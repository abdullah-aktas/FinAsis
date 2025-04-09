from rest_framework import serializers
from .models import EInvoice, EArchive, BankIntegration

class EInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EInvoice
        fields = [
            'id', 'invoice_number', 'created_at', 'updated_at',
            'status', 'sender', 'receiver_vkn', 'receiver_name',
            'amount', 'currency', 'pdf_file', 'xml_file'
        ]
        read_only_fields = ['invoice_number', 'created_at', 'updated_at']

    def validate_receiver_vkn(self, value):
        if len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError("Geçersiz VKN formatı")
        return value

class EArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = EArchive
        fields = [
            'id', 'archive_number', 'created_at', 'updated_at',
            'status', 'document_type', 'document_date',
            'document_owner', 'file', 'ocr_content', 'metadata'
        ]
        read_only_fields = ['archive_number', 'created_at', 'updated_at', 'ocr_content']

    def validate_file(self, value):
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Desteklenmeyen dosya türü. PDF, JPEG veya PNG yükleyin."
            )
        return value

class BankIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankIntegration
        fields = [
            'id', 'bank', 'account_holder', 'account_number',
            'iban', 'is_active', 'last_sync', 'balance'
        ]
        read_only_fields = ['last_sync', 'balance']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True}
        }

    def validate_iban(self, value):
        # IBAN formatını kontrol et
        value = value.replace(' ', '')
        if not (value.startswith('TR') and len(value) == 26):
            raise serializers.ValidationError("Geçersiz IBAN formatı")
        return value

class BankTransactionSerializer(serializers.Serializer):
    id = serializers.CharField()
    date = serializers.DateTimeField()
    description = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    type = serializers.ChoiceField(choices=['CREDIT', 'DEBIT'])
    balance_after = serializers.DecimalField(max_digits=15, decimal_places=2)
    currency = serializers.CharField(default='TRY')
    status = serializers.CharField()
    reference = serializers.CharField(allow_null=True)
    category = serializers.CharField(allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Pozitif/negatif değerleri düzenle
        if data['type'] == 'DEBIT':
            data['amount'] = -abs(data['amount'])
        return data 