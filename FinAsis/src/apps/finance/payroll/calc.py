from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class PayrollInput:
    gross: Decimal
    sgk_rate: Decimal = Decimal("0.14")
    stamp_tax_rate: Decimal = Decimal("0.00759")
    income_tax_rate: Decimal = Decimal("0.15")


@dataclass(slots=True)
class PayrollResult:
    sgk: Decimal
    income_tax: Decimal
    stamp_tax: Decimal
    net: Decimal


def compute_payroll(p: PayrollInput) -> PayrollResult:
    sgk = (p.gross * p.sgk_rate).quantize(Decimal("0.01"))
    stamp_tax = (p.gross * p.stamp_tax_rate).quantize(Decimal("0.01"))
    taxable = p.gross - sgk
    income_tax = (taxable * p.income_tax_rate).quantize(Decimal("0.01"))
    net = p.gross - sgk - stamp_tax - income_tax
    return PayrollResult(sgk=sgk, income_tax=income_tax, stamp_tax=stamp_tax, net=net)
