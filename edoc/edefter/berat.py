from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List

try:
    from lxml import etree  # type: ignore
except Exception:  # pragma: no cover - fallback if lxml missing
    import xml.etree.ElementTree as etree  # type: ignore


NS_EDEFTER = "http://edefter.gov.tr/namespace"


def _to_bytes(elem) -> bytes:
    try:
        return etree.tostring(elem, xml_declaration=True, encoding="UTF-8", pretty_print=True)  # type: ignore[call-arg]
    except TypeError:
        return etree.tostring(elem, encoding="utf-8")


@dataclass(slots=True)
class JournalEntry:
    date: date
    number: str
    debit: float
    credit: float


def compute_hash_chain(entries: Iterable[JournalEntry]) -> List[str]:
    """Compute a simple SHA-256 hash chain over journal entries.

    Hash input format (stable): ISO date | number | debit(2dp) | credit(2dp)
    """
    chain: List[str] = []
    prev = b""
    for e in entries:
        payload = (
            f"{e.date.isoformat()}|{e.number}|{e.debit:.2f}|{e.credit:.2f}".encode()
        )
        h = hashlib.sha256(prev + payload).hexdigest()
        chain.append(h)
        prev = h.encode()
    return chain


def build_berat_xml(
    period: str, company_vkn: str, last_hash: str, *, defter_type: str = "YEVMIYE"
) -> bytes:
    """Build a minimal e-Defter berat XML snippet.

    Parameters
    - period: YYYY-MM
    - company_vkn: Turkish tax number
    - last_hash: hex string of the last journal hash in the period
    - defter_type: YEVMIYE | KEBIR (string, simplified)
    """
    # xml.etree.ElementTree lacks nsmap/QName like lxml; prefer namespaced tag strings.
    ef = f"{{{NS_EDEFTER}}}"
    try:
        root = etree.Element(ef + "Berat")
        etree.SubElement(root, ef + "Period").text = period
        etree.SubElement(root, ef + "CompanyVKN").text = company_vkn
        etree.SubElement(root, ef + "DefterType").text = defter_type
        etree.SubElement(root, ef + "LastHash").text = last_hash
        return _to_bytes(root)
    except Exception:
        # Last-resort: produce un-namespaced simple XML
        root = etree.Element("Berat")
        etree.SubElement(root, "Period").text = period
        etree.SubElement(root, "CompanyVKN").text = company_vkn
        etree.SubElement(root, "DefterType").text = defter_type
        etree.SubElement(root, "LastHash").text = last_hash
        return _to_bytes(root)


def validate_berat_xml(xml_bytes: bytes) -> None:
    """Placeholder for XSD validation.

    In Sprint 1, we skip strict XSD due to schema licensing; this hook allows
    plugging in lxml XMLSchema validation when XSD is available.
    """
    # In future: parse schema from configured path and validate.
    # nosec: B314
    etree.fromstring(xml_bytes)  # basic well-formedness check
