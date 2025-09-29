# -*- coding: utf-8 -*-
import pytest
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError

from src.apps.accounting.models import Company
from src.apps.finance.enhanced_accounting_models import (
    ChartOfAccounts, FiscalPeriod, JournalVoucher, JournalEntry, TrialBalanceSnapshot
)

@pytest.mark.django_db
def test_trial_balance_snapshot_basic(django_user_model):
    user = django_user_model.objects.create(username='u1')
    company = Company.objects.create(name='Test Co', tax_number='1234567890')
    period = FiscalPeriod.objects.create(company=company, name='2025', start_date=timezone.now().date().replace(month=1, day=1), end_date=timezone.now().date().replace(month=12, day=31))
    # Accounts
    a1 = ChartOfAccounts.objects.create(company=company, code='100', name='Kasa', account_type='1', is_detail_account=True)
    a2 = ChartOfAccounts.objects.create(company=company, code='600', name='Satış Geliri', account_type='6', is_detail_account=True)
    # Voucher
    v = JournalVoucher.objects.create(company=company, voucher_number='JV1', voucher_type='GENERAL', date=timezone.now().date(), fiscal_period=period, description='Test')
    JournalEntry.objects.create(voucher=v, line_number=1, account=a1, debit_amount=Decimal('100'), description='cash in')
    JournalEntry.objects.create(voucher=v, line_number=2, account=a2, credit_amount=Decimal('100'), description='revenue')
    v.post(user)

    snapshot = TrialBalanceSnapshot.build_snapshot(company, period, as_of_date=timezone.now().date(), user=user)
    assert '100' in snapshot.account_balances
    assert snapshot.total_debits == Decimal('100')
    assert snapshot.total_credits == Decimal('100')

@pytest.mark.django_db
def test_closed_period_block(django_user_model):
    user = django_user_model.objects.create(username='u2')
    company = Company.objects.create(name='Test Co2', tax_number='1234567891')
    period = FiscalPeriod.objects.create(company=company, name='2025', start_date=timezone.now().date().replace(month=1, day=1), end_date=timezone.now().date().replace(month=12, day=31), is_closed=True)
    a1 = ChartOfAccounts.objects.create(company=company, code='101', name='Banka', account_type='1', is_detail_account=True)
    with pytest.raises(ValidationError):
        JournalVoucher.objects.create(company=company, voucher_number='JV2', voucher_type='GENERAL', date=timezone.now().date(), fiscal_period=period, description='Should fail')
