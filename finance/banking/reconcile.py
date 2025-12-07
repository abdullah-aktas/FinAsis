from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, List, Tuple, Optional


@dataclass(slots=True)
class BankTxn:
    id: str
    amount: Decimal
    date: date
    description: str = ""
    counter_iban: Optional[str] = None


@dataclass(slots=True)
class LedgerItem:
    id: str
    amount: Decimal
    date: date
    description: str = ""
    counter_iban: Optional[str] = None


def _token_overlap(a: str, b: str) -> float:
    at = {t for t in a.lower().split() if len(t) > 2}
    bt = {t for t in b.lower().split() if len(t) > 2}
    if not at or not bt:
        return 0.0
    inter = at & bt
    union = at | bt
    return len(inter) / len(union)


def score_match(
    txn: BankTxn,
    cand: LedgerItem,
    *,
    amount_tol: Decimal = Decimal("0.01"),
    date_window_days: int = 3,
) -> float:
    score = 0.0
    # Amount score (60 pts): within tolerance -> full, else 0
    if abs(txn.amount - cand.amount) <= amount_tol:
        score += 60.0
    # Date proximity (up to 20 pts)
    d = abs((txn.date - cand.date).days)
    if d <= date_window_days:
        score += 20.0 * (1 - d / max(1, date_window_days))
    # IBAN (20 pts)
    if (
        txn.counter_iban
        and cand.counter_iban
        and txn.counter_iban.replace(" ", "") == cand.counter_iban.replace(" ", "")
    ):
        score += 20.0
    # Description token overlap (up to 15 pts) but cap overall at 100
    score += 15.0 * _token_overlap(txn.description, cand.description)
    return min(score, 100.0)


def reconcile(
    bank_txns: Iterable[BankTxn],
    ledger_items: Iterable[LedgerItem],
    *,
    min_score: float = 60.0,
) -> List[Tuple[str, str, float]]:
    """Greedy one-to-one matching based on score.

    Returns list of (bank_txn_id, ledger_item_id, score).
    """
    txns = list(bank_txns)
    cands = list(ledger_items)
    taken: set[str] = set()
    matches: List[Tuple[str, str, float]] = []
    for t in txns:
        best: Tuple[str, float] | None = None
        for c in cands:
            if c.id in taken:
                continue
            s = score_match(t, c)
            if s >= min_score:
                if (
                    best is None
                    or s > best[1]
                    or (
                        s == best[1]
                        and abs(
                            (
                                t.date
                                - next(
                                    x
                                    for x in cands
                                    if x.id == (best[0] if best else c.id)
                                ).date
                            ).days
                        )
                        > abs((t.date - c.date).days)
                    )
                ):
                    best = (c.id, s)
        if best:
            taken.add(best[0])
            matches.append((t.id, best[0], best[1]))
    return matches
