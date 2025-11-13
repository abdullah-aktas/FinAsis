from rest_framework import serializers
from finance.enhanced_accounting_models import JournalVoucher, JournalEntry, ChartOfAccounts

class JournalEntryInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = [
            'line_number', 'account', 'description', 'debit_amount', 'credit_amount',
            'cost_center', 'project_code', 'currency_code', 'exchange_rate'
        ]

class JournalVoucherSerializer(serializers.ModelSerializer):
    journal_entries = JournalEntryInlineSerializer(many=True, write_only=True, required=True)
    is_balanced = serializers.BooleanField(read_only=True)
    total_debit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_credit = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = JournalVoucher
        fields = [
            'id', 'company', 'voucher_number', 'voucher_type', 'date', 'fiscal_period',
            'description', 'reference_number', 'total_debit', 'total_credit', 'is_balanced',
            'is_posted', 'journal_entries'
        ]
        read_only_fields = ['is_posted']

    def validate(self, attrs):
        entries = attrs.get('journal_entries', [])
        debit_sum = sum([e.get('debit_amount', 0) for e in entries])
        credit_sum = sum([e.get('credit_amount', 0) for e in entries])
        if debit_sum != credit_sum:
            raise serializers.ValidationError('Borç ve alacak toplamları eşit olmalı.')
        return attrs

    def create(self, validated_data):
        entries_data = validated_data.pop('journal_entries')
        user = self.context['request'].user
        voucher = JournalVoucher.objects.create(created_by=user, **validated_data)
        # line_number otomatik sırala
        for idx, entry in enumerate(entries_data, start=1):
            JournalEntry.objects.create(voucher=voucher, line_number=idx, **entry)
        # Totalleri hesapla
        voucher.calculate_totals(save=True)
        return voucher
