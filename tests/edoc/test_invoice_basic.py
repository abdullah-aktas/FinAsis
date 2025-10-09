import datetime as dt
from decimal import Decimal

from edoc.ubltr.invoice import Invoice, Party, Line
from edoc.ubltr.schema import validate_invoice_xml


def test_minimal_invoice_xml_builds_and_validates():
    inv = Invoice(
        id="INV-1001",
        issue_date=dt.date(2025, 1, 15),
        supplier=Party(name="Tedarikçi A.Ş.", tax_id="1234567890"),
        customer=Party(name="Müşteri Ltd.", tax_id="0987654321"),
        lines=[
            Line(description="Ürün", quantity=Decimal("2"), unit_price=Decimal("150.00")),
        ],
    )
    xmlb = inv.to_xml_bytes()
    assert b"<Invoice" in xmlb
    # Validation skips if schemas not present; should not raise
    validate_invoice_xml(xmlb)
