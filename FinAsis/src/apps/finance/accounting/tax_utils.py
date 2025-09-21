# -*- coding: utf-8 -*-
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class VatResult:
    base: Decimal
    rate: Decimal
    tax: Decimal
    total: Decimal


def calculate_vat(base: Decimal, rate: Decimal) -> VatResult:
    tax = (base * rate).quantize(Decimal('0.01'))
    total = base + tax
    return VatResult(base=base, rate=rate, tax=tax, total=total)


@dataclass
class WithholdingResult:
    base: Decimal
    vat_rate: Decimal
    vat_total: Decimal
    seller_share: Decimal
    buyer_share: Decimal
    buyer_withholding_rate: Decimal


def calculate_vat_with_withholding(base: Decimal, vat_rate: Decimal, buyer_withholding_rate: Decimal) -> WithholdingResult:
    """Tevkifatlı KDV: vat_total = base*vat_rate; alıcı payı = vat_total*buyer_withholding_rate."""
    vat_total = (base * vat_rate).quantize(Decimal('0.01'))
    buyer_share = (vat_total * buyer_withholding_rate).quantize(Decimal('0.01'))
    seller_share = vat_total - buyer_share
    return WithholdingResult(
        base=base,
        vat_rate=vat_rate,
        vat_total=vat_total,
        seller_share=seller_share,
        buyer_share=buyer_share,
        buyer_withholding_rate=buyer_withholding_rate,
    )


