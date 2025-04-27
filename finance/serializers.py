"""
Finance Modülü - Serializer Sınıfları
---------------------
Bu dosya, Finance modülünün serializer sınıflarını içerir.
"""

from rest_framework import serializers
from .models import Transaction, Budget

class TransactionSerializer(serializers.ModelSerializer):
    """
    Finansal işlem serializer'ı.
    """
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'type', 'category',
            'description', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_amount(self, value):
        """
        Miktar değerinin pozitif olmasını sağlar.
        """
        if value <= 0:
            raise serializers.ValidationError("Miktar pozitif olmalıdır.")
        return value

class BudgetSerializer(serializers.ModelSerializer):
    """
    Bütçe serializer'ı.
    """
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'amount',
            'start_date', 'end_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """
        Bütçe tarihlerinin geçerli olmasını sağlar.
        """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError(
                "Başlangıç tarihi bitiş tarihinden önce olmalıdır."
            )
        return data 