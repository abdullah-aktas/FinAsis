from datetime import date
from decimal import Decimal

from FinAsis.src.apps.finance.banking.reconcile import BankTxn, LedgerItem, reconcile


def test_simple_reconcile_match():
    txns = [BankTxn(id="t1", amount=Decimal("100.00"), date=date(2025, 9, 10), description="POS ABC", counter_iban=None)]
    cands = [LedgerItem(id="l1", amount=Decimal("100.00"), date=date(2025, 9, 11), description="POS Tahsilat ABC")]
    matches = reconcile(txns, cands, min_score=50.0)
    assert matches and matches[0][0] == "t1" and matches[0][1] == "l1"