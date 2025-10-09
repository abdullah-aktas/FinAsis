from __future__ import annotations

from datetime import date
from decimal import Decimal

from edoc.ubltr.invoice import (
    Invoice,
    Party,
    Line,
    TaxTotal,
    TaxSubtotal,
    AllowanceCharge,
    PaymentMeans,
    Withholding,
)
from edoc.ubltr.schema import validate_invoice_xml


def test_invoice_fields_basic_xml_and_totals():
    inv = Invoice(
        id="INV-1001",
        issue_date=date(2025, 10, 9),
        supplier=Party(name="Tedarikçi AŞ", tax_id="1111111111"),
        customer=Party(name="Müşteri Ltd", tax_id="2222222222"),
        currency="TRY",
        lines=[
            Line(description="Ürün 1", quantity=Decimal("2"), unit_price=Decimal("100")),
            Line(description="Ürün 2", quantity=Decimal("1"), unit_price=Decimal("50")),
        ],
        notes=["e-Arşiv Notu: Teşekkürler"],
        allowance_charges=[
            AllowanceCharge(charge_indicator=False, amount=Decimal("10.00"), reason="İskonto"),
            AllowanceCharge(charge_indicator=True, amount=Decimal("5.00"), reason="Kargo"),
        ],
        tax_total=TaxTotal(
            tax_amount=Decimal("29.00"),
            subtotals=[
                TaxSubtotal(taxable_amount=Decimal("250.00"), tax_amount=Decimal("29.00"), percent=Decimal("11.6")),
            ],
        ),
        payment_means=PaymentMeans(code="42", payee_iban="TR000000000000000000000000"),
        withholding_tax_total=Withholding(tax_amount=Decimal("2.50"), taxable_amount=Decimal("50.00"), reason="Tevkifat"),
    )

    xml = inv.to_xml_bytes()
    # basic sanity
    assert b"Invoice" in xml and b"PayableAmount" in xml and b"TaxTotal" in xml

    # totals: base = 2*100 + 1*50 = 250; -10 +5 => 245; +29 => 274; -2.5 => 271.5
    # rounded to 2 decimals
    assert b">271.50<" in xml

    # Validate (no-op if schemas not present)
    validate_invoice_xml(xml)
