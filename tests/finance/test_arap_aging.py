from datetime import date
from decimal import Decimal

from FinAsis.src.apps.finance.arap.aging import ARAPItem, aging_buckets


def test_aging_buckets():
    today = date(2025, 10, 1)
    items = [
        ARAPItem(id="1", due_date=date(2025, 10, 5), amount=Decimal("100")),
        ARAPItem(id="2", due_date=date(2025, 9, 10), amount=Decimal("200")),
        ARAPItem(id="3", due_date=date(2025, 8, 20), amount=Decimal("300")),
        ARAPItem(id="4", due_date=date(2025, 6, 1), amount=Decimal("400")),
    ]
    buckets = aging_buckets(items, today)
    assert buckets["current"] == Decimal("100")
    assert buckets["30"] >= Decimal("200")