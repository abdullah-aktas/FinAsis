# -*- coding: utf-8 -*-
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class FxDiffResult:
    invoice_value_local: Decimal
    payment_value_local: Decimal
    difference_local: Decimal  # pozitif: gelir (646), negatif: gider (656)


def compute_fx_difference(invoice_amount_fx: Decimal, invoice_rate: Decimal, payment_amount_fx: Decimal, payment_rate: Decimal) -> FxDiffResult:
    """Fatura ve ödeme kuruna göre kur farkını (yerel para) hesaplar."""
    inv_local = (invoice_amount_fx * invoice_rate).quantize(Decimal('0.01'))
    pay_local = (payment_amount_fx * payment_rate).quantize(Decimal('0.01'))
    diff = (pay_local - inv_local).quantize(Decimal('0.01'))
    return FxDiffResult(
        invoice_value_local=inv_local,
        payment_value_local=pay_local,
        difference_local=diff,
    )


