"""
Banka işlemleri serileştiricileri
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.finance.models import BankAccount, Transaction, TransactionCategory

class BankAccountSerializer(serializers.ModelSerializer):
    """Banka hesabı serileştirici"""
    
    user_display = serializers.SerializerMethodField()
    
    class Meta:
        model = BankAccount
        fields = ['id', 'bank_name', 'account_number', 'iban', 'account_type', 
                 'currency', 'balance', 'description', 'user', 'user_display', 
                 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'user', 'user_display', 'created_at', 'updated_at']
    
    def get_user_display(self, obj):
        """Kullanıcının görüntüleme adını döndür"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
        return None

class TransactionCategorySerializer(serializers.ModelSerializer):
    """İşlem kategorisi serileştirici"""
    
    class Meta:
        model = TransactionCategory
        fields = ['id', 'name', 'description', 'parent', 'type', 'color']

class TransactionSerializer(serializers.ModelSerializer):
    """İşlem serileştirici"""
    
    category_display = serializers.SerializerMethodField()
    source_account_display = serializers.SerializerMethodField()
    destination_account_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'date', 'category', 
                 'category_display', 'description', 'source_account', 
                 'source_account_display', 'destination_account', 
                 'destination_account_display', 'reference_number', 
                 'created_at', 'updated_at', 'status']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_category_display(self, obj):
        """Kategori adını döndür"""
        return obj.category.name if obj.category else None
    
    def get_source_account_display(self, obj):
        """Kaynak hesap adını döndür"""
        if obj.source_account:
            return f"{obj.source_account.bank_name} - {obj.source_account.account_number}"
        return None
    
    def get_destination_account_display(self, obj):
        """Hedef hesap adını döndür"""
        if obj.destination_account:
            return f"{obj.destination_account.bank_name} - {obj.destination_account.account_number}"
        return None
    
    def validate(self, data):
        """İşlem verilerini doğrula"""
        # İşlem türüne göre zorunlu alanları kontrol et
        transaction_type = data.get('transaction_type')
        source_account = data.get('source_account')
        destination_account = data.get('destination_account')
        
        if transaction_type == 'transfer' and not (source_account and destination_account):
            raise serializers.ValidationError(
                _("Transfer işlemleri için kaynak ve hedef hesap gereklidir.")
            )
        
        if transaction_type == 'expense' and not source_account:
            raise serializers.ValidationError(
                _("Harcama işlemleri için kaynak hesap gereklidir.")
            )
        
        if transaction_type == 'income' and not destination_account:
            raise serializers.ValidationError(
                _("Gelir işlemleri için hedef hesap gereklidir.")
            )
        
        # Negatif tutar kontrolü
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError(
                _("İşlem tutarı sıfırdan büyük olmalıdır.")
            )
        
        return data 