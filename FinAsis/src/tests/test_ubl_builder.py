from __future__ import annotations

from src.apps.submissions.ubl import build_ubl_invoice_xml, validate_xml_against_xsd


def test_build_ubl_invoice_xml_minimal():
    xml = build_ubl_invoice_xml(
        code="INV-1",
        period="2025-10-11",
        taxpayer_vkn_tckn="1234567890",
        payload={"total": 100},
    )
    assert xml.startswith(b"<?xml") and b"Invoice" in xml and b"CustomizationID" in xml
    # Schema validation should be graceful (schemas likely absent in CI)
    errs = validate_xml_against_xsd(xml, schemas_dir=None)
    assert errs == []
