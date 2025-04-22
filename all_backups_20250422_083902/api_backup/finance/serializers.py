from rest_framework import serializers
from finance.models import Transaction, CashFlow, IncomeStatement

class TransactionSerializer(serializers.ModelSerializer):
    """
    Finansal işlemler için serializer.
    """
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'amount', 'currency', 'date',
            'description', 'reference_number', 'status', 'created_at',
            'updated_at', 'approved_by', 'rejected_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'approved_by', 'rejected_by']

class CashFlowSerializer(serializers.ModelSerializer):
    """
    Nakit akışı işlemleri için serializer.
    """
    class Meta:
        model = CashFlow
        fields = [
            'id', 'flow_type', 'amount', 'currency', 'date',
            'description', 'period', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class IncomeStatementSerializer(serializers.ModelSerializer):
    """
    Gelir tablosu işlemleri için serializer.
    """
    class Meta:
        model = IncomeStatement
        fields = [
            'id', 'period', 'year', 'total_revenue', 'total_expenses',
            'net_income', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 