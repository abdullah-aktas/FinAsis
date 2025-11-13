# -*- coding: utf-8 -*-
from decimal import Decimal

import pytest
from django.utils import timezone

from accounting.models import Company
from finance.accounting.models import AccountType, Account, VoucherType, PostingRule
from finance.accounting.services import post_document, DocumentLineContext
from finance.accounting.tax_utils import calculate_vat, calculate_vat_with_withholding
from finance.accounting.inventory_fifo import StockLayer, fifo_consume


@pytest.mark.django_db
def test_posting_rule_creates_balanced_voucher():
    company = Company.objects.create(name="Test", tax_number="1234567890")
    at = AccountType.objects.create(code="A", name="Varlık")
    rt = AccountType.objects.create(code="R", name="Gelir")
    tt = AccountType.objects.create(code="T", name="Vergi")

    Account.objects.create(company=company, code="100", name="Kasa", type=at)
    Account.objects.create(company=company, code="600", name="Satış Gelirleri", type=rt)
    Account.objects.create(company=company, code="391", name="Hesaplanan KDV", type=tt)

    vt = VoucherType.objects.create(code="MA", name="Mahsup")

    PostingRule.objects.create(
        company=company,
        name="SATIS_%20",
        document_type="sales_invoice",
        priority=10,
        definition={
            'condition': {'tax_rate_eq': 0.20},
            'lines': [
                { 'side': 'D', 'account': '100', 'formula': 'gross' },
                { 'side': 'C', 'account': '600', 'formula': 'net' },
                { 'side': 'C', 'account': '391', 'formula': 'net*tax_rate' },
            ]
        }
    )

    fiscal_year = type('FY', (), {'id': 1})()  # dummy
    ctx = [DocumentLineContext(description="Satış", net_amount=Decimal('100'), tax_rate=Decimal('0.20'), currency='TRY')]
    voucher = post_document(company, fiscal_year, 'sales_invoice', 'TST-1', timezone.now().date(), 'TRY', ctx)
    assert voucher.state == 'posted'
    assert voucher.is_balanced()


@pytest.mark.django_db
def test_vat_and_fifo_helpers():
    v = calculate_vat(Decimal('100'), Decimal('0.20'))
    assert v.tax == Decimal('20.00') and v.total == Decimal('120.00')

    w = calculate_vat_with_withholding(Decimal('100'), Decimal('0.20'), Decimal('0.50'))
    assert w.vat_total == Decimal('20.00') and w.buyer_share == Decimal('10.00')

    layers = [StockLayer(quantity=Decimal('5'), unit_cost=Decimal('10')), StockLayer(quantity=Decimal('10'), unit_cost=Decimal('12'))]
    res = fifo_consume(layers, Decimal('8'))
    assert res.cost_of_issued == Decimal('5')*Decimal('10') + Decimal('3')*Decimal('12')

