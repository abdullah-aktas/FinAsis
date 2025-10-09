from __future__ import annotations

from datetime import date

from edoc.ubltr.dispatch import DispatchAdvice, DispatchParty
from edoc.ubltr.schema import validate_dispatch_xml, has_dispatch_schema


def test_dispatch_minimal_build_and_validate():
    da = DispatchAdvice(
        id="DA-1",
        issue_date=date(2025, 10, 9),
        supplier=DispatchParty(name="Tedarikçi AŞ"),
        customer=DispatchParty(name="Müşteri Ltd"),
    )
    xml = da.to_xml_bytes()
    assert b"DispatchAdvice" in xml and b"DespatchSupplierParty" in xml

    # Validate (skip if schemas not present)
    validate_dispatch_xml(xml)
