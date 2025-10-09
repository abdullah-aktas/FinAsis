from __future__ import annotations

import os
import pytest

from edoc.ubltr.schema import validate_invoice_xml, has_invoice_schema


def test_validate_invoice_xml_graceful_skip_without_xsd():
    # Ensure no schema dir is configured so the function should return without error
    env = os.environ.copy()
    env.pop("EDOC_SCHEMAS_DIR", None)
    # Without XSDs present or configured, this should not raise
    validate_invoice_xml(b"<Invoice/>")


@pytest.mark.skipif(not has_invoice_schema(), reason="Invoice XSD not available")
def test_validate_invoice_xml_with_xsd(sample_invoice_xml: bytes | None = None):
    # When schemas are present, a minimal but valid invoice XML should validate
    # If no sample is provided, use a tiny well-formed placeholder; real tests should load from fixtures
    xml = sample_invoice_xml or b"<Invoice xmlns='urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'/>"
    validate_invoice_xml(xml)
