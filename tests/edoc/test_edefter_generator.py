from decimal import Decimal
from datetime import date

from FinAsis.src.edoc.edefter.generator import JournalEntryDTO, JournalLine, build_yevmiye, build_kebir


def test_build_yevmiye_totals():
    entries = [
        JournalEntryDTO(
            date_=date(2025, 9, 1),
            number="1",
            lines=[
                JournalLine("100", debit=Decimal("100.00"), description="Cash"),
                JournalLine("600", credit=Decimal("100.00"), description="Sales"),
            ],
        ),
        JournalEntryDTO(
            date_=date(2025, 9, 2),
            number="2",
            lines=[
                JournalLine("770", debit=Decimal("50.00"), description="Expense"),
                JournalLine("100", credit=Decimal("50.00"), description="Cash"),
            ],
        ),
    ]
    xml = build_yevmiye(entries).decode()
    assert "<Totals>" in xml
    assert "<TotalDebit>150.00</TotalDebit>" in xml
    assert "<TotalCredit>150.00</TotalCredit>" in xml


def test_build_kebir_balances():
    entries = [
        JournalEntryDTO(
            date_=date(2025, 9, 1),
            number="1",
            lines=[
                JournalLine("100", debit=Decimal("100.00")),
                JournalLine("600", credit=Decimal("100.00")),
            ],
        ),
        JournalEntryDTO(
            date_=date(2025, 9, 2),
            number="2",
            lines=[
                JournalLine("770", debit=Decimal("50.00")),
                JournalLine("100", credit=Decimal("50.00")),
            ],
        ),
    ]
    xml = build_kebir(entries).decode()
    # account 100: 100 debit - 50 credit = 50
    assert "<Code>100</Code>" in xml
    assert "<Balance>50.00</Balance>" in xml
