from rest_framework import serializers
from accounting.models import JournalEntry, AccountPlan, BalanceSheet

class JournalEntrySerializer(serializers.ModelSerializer):
    """
    Muhasebe kayıtları için serializer.
    """
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_type', 'date', 'reference_number',
            'description', 'debit_account', 'credit_account',
            'amount', 'status', 'created_at', 'updated_at',
            'posted_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'posted_by']

class AccountPlanSerializer(serializers.ModelSerializer):
    """
    Hesap planı işlemleri için serializer.
    """
    class Meta:
        model = AccountPlan
        fields = [
            'id', 'account_code', 'account_name', 'account_type',
            'parent_account', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class BalanceSheetSerializer(serializers.ModelSerializer):
    """
    Bilanço işlemleri için serializer.
    """
    class Meta:
        model = BalanceSheet
        fields = [
            'id', 'period', 'year', 'total_assets',
            'total_liabilities', 'total_equity', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 