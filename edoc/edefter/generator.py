from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, List

try:
    from lxml import etree  # type: ignore
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as etree  # type: ignore


@dataclass(slots=True)
class JournalLine:
    account: str
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    description: str = ""


@dataclass(slots=True)
class JournalEntryDTO:
    date_: date
    number: str
    lines: List[JournalLine]


def build_yevmiye(entries: Iterable[JournalEntryDTO]) -> bytes:
    root = etree.Element("Yevmiye")
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    for e in entries:
        je = etree.SubElement(root, "Entry")
        etree.SubElement(je, "Date").text = e.date_.isoformat()
        etree.SubElement(je, "Number").text = e.number
        for ln in e.lines:
            line_elem = etree.SubElement(je, "Line")
            etree.SubElement(line_elem, "Account").text = ln.account
            etree.SubElement(line_elem, "Debit").text = f"{ln.debit:.2f}"
            etree.SubElement(line_elem, "Credit").text = f"{ln.credit:.2f}"
            etree.SubElement(line_elem, "Description").text = ln.description
            total_debit += ln.debit
            total_credit += ln.credit
    totals = etree.SubElement(root, "Totals")
    etree.SubElement(totals, "TotalDebit").text = f"{total_debit:.2f}"
    etree.SubElement(totals, "TotalCredit").text = f"{total_credit:.2f}"
    try:
        return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)  # type: ignore[call-arg]
    except TypeError:
        return etree.tostring(root, encoding="utf-8")


def build_kebir(entries: Iterable[JournalEntryDTO]) -> bytes:
    # very small grouping by account
    balances: dict[str, Decimal] = {}
    for e in entries:
        for ln in e.lines:
            balances[ln.account] = (
                balances.get(ln.account, Decimal("0.00")) + ln.debit - ln.credit
            )
    root = etree.Element("Kebir")
    for acc in sorted(balances.keys()):
        a = etree.SubElement(root, "Account")
        etree.SubElement(a, "Code").text = acc
        etree.SubElement(a, "Balance").text = f"{balances[acc]:.2f}"
    try:
        return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)  # type: ignore[call-arg]
    except TypeError:
        return etree.tostring(root, encoding="utf-8")
