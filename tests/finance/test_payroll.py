from decimal import Decimal

from FinAsis.src.apps.finance.payroll.calc import PayrollInput, compute_payroll


def test_compute_payroll_basic():
    res = compute_payroll(PayrollInput(gross=Decimal("10000")))
    assert res.net > Decimal("0")
    assert res.sgk > Decimal("0")