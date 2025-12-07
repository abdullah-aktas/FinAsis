from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Dict


@dataclass(slots=True)
class ARAPItem:
    id: str
    due_date: date
    amount: Decimal


def aging_buckets(items: Iterable[ARAPItem], today: date) -> Dict[str, Decimal]:
    buckets = {
        "current": Decimal("0"),
        "30": Decimal("0"),
        "60": Decimal("0"),
        "90": Decimal("0"),
        "120+": Decimal("0"),
    }
    for it in items:
        delta = (today - it.due_date).days
        if delta <= 0:
            buckets["current"] += it.amount
        elif delta <= 30:
            buckets["30"] += it.amount
        elif delta <= 60:
            buckets["60"] += it.amount
        elif delta <= 90:
            buckets["90"] += it.amount
        else:
            buckets["120+"] += it.amount
    return buckets
