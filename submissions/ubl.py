from __future__ import annotations
from typing import List
import lxml.etree as ET

from django.conf import settings


def build_ubl_invoice_xml(
    *, code: str, period: str, taxpayer_vkn_tckn: str, payload: dict | None
) -> bytes:
    """
    Build a minimal UBL 2.1 Invoice XML (TR profile/customization) skeleton from declaration-like fields.

    Note: This is a minimal envelope sufficient for integration smoke tests. Real projects should
    map full payload to UBL structures (cac:AccountingSupplierParty, cac:AccountingCustomerParty, lines, taxes...).
    """

    nsmap = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    }

    root = ET.Element("Invoice", nsmap=nsmap)

    profile_id = getattr(settings, "EDOC_PROFILE_ID", "TICARIFATURA")
    customization_id = getattr(settings, "EDOC_CUSTOMIZATION_ID", "TR1.2")

    cbc_profile = ET.SubElement(root, ET.QName(nsmap["cbc"], "ProfileID"))
    cbc_profile.text = profile_id

    cbc_custom = ET.SubElement(root, ET.QName(nsmap["cbc"], "CustomizationID"))
    cbc_custom.text = customization_id

    cbc_id = ET.SubElement(root, ET.QName(nsmap["cbc"], "ID"))
    cbc_id.text = code

    cbc_issue_date = ET.SubElement(root, ET.QName(nsmap["cbc"], "IssueDate"))
    # Use period as a date-like string when possible; otherwise fallback to YYYY-01-01 for bare years
    if len(period) == 10 and "-" in period:
        cbc_issue_date.text = period
    elif len(period) == 7 and "-" in period:
        cbc_issue_date.text = period + "-01"
    else:
        cbc_issue_date.text = period[:4] + "-01-01"

    # Currency & UUID if provided
    currency = (payload or {}).get("currency") if payload else None
    if currency:
        cbc_doc_currency = ET.SubElement(
            root, ET.QName(nsmap["cbc"], "DocumentCurrencyCode")
        )
        cbc_doc_currency.text = str(currency)

    uuid = (payload or {}).get("uuid") if payload else None
    if uuid:
        cbc_uuid = ET.SubElement(root, ET.QName(nsmap["cbc"], "UUID"))
        cbc_uuid.text = str(uuid)

    # Supplier (AccountingSupplierParty)
    cac_supplier = ET.SubElement(
        root, ET.QName(nsmap["cac"], "AccountingSupplierParty")
    )
    cac_supplier_party = ET.SubElement(cac_supplier, ET.QName(nsmap["cac"], "Party"))
    supplier = (payload or {}).get("supplier") if payload else None
    if isinstance(supplier, dict):
        # EndpointID carries VKN/TCKN in many TR profiles
        endpoint = ET.SubElement(
            cac_supplier_party, ET.QName(nsmap["cbc"], "EndpointID")
        )
        endpoint.text = str(supplier.get("vkn_tckn") or taxpayer_vkn_tckn)
        party_name = supplier.get("name")
        if party_name:
            cac_party_name = ET.SubElement(
                cac_supplier_party, ET.QName(nsmap["cac"], "PartyName")
            )
            cbc_name = ET.SubElement(cac_party_name, ET.QName(nsmap["cbc"], "Name"))
            cbc_name.text = str(party_name)
    else:
        endpoint = ET.SubElement(
            cac_supplier_party, ET.QName(nsmap["cbc"], "EndpointID")
        )
        endpoint.text = taxpayer_vkn_tckn

    # Customer (AccountingCustomerParty)
    customer = (payload or {}).get("customer") if payload else None
    if isinstance(customer, dict):
        cac_customer = ET.SubElement(
            root, ET.QName(nsmap["cac"], "AccountingCustomerParty")
        )
        cac_customer_party = ET.SubElement(
            cac_customer, ET.QName(nsmap["cac"], "Party")
        )
        endpoint = ET.SubElement(
            cac_customer_party, ET.QName(nsmap["cbc"], "EndpointID")
        )
        endpoint.text = str(customer.get("vkn_tckn") or "")
        party_name = customer.get("name")
        if party_name:
            cac_party_name = ET.SubElement(
                cac_customer_party, ET.QName(nsmap["cac"], "PartyName")
            )
            cbc_name = ET.SubElement(cac_party_name, ET.QName(nsmap["cbc"], "Name"))
            cbc_name.text = str(party_name)

    # Lines (optional, very minimal)
    total_tax_amt = 0.0
    line_total = 0.0
    lines = (payload or {}).get("lines") if isinstance(payload, dict) else None
    if isinstance(lines, list):
        for idx, line in enumerate(lines, start=1):
            if not isinstance(line, dict):
                continue
            qty = float(line.get("quantity", 1))
            price = float(line.get("price", 0.0))
            tax_rate = float(line.get("tax_rate", 0.0))
            ext = qty * price
            tax_amt = ext * (tax_rate / 100.0)
            line_total += ext
            total_tax_amt += tax_amt

            il = ET.SubElement(root, ET.QName(nsmap["cac"], "InvoiceLine"))
            ET.SubElement(il, ET.QName(nsmap["cbc"], "ID")).text = str(idx)
            ET.SubElement(il, ET.QName(nsmap["cbc"], "InvoicedQuantity")).text = str(
                qty
            )
            ET.SubElement(il, ET.QName(nsmap["cbc"], "LineExtensionAmount")).text = (
                f"{ext:.2f}"
            )
            # Item name (optional)
            item_name = line.get("name")
            if item_name:
                item = ET.SubElement(il, ET.QName(nsmap["cac"], "Item"))
                ET.SubElement(item, ET.QName(nsmap["cbc"], "Name")).text = str(
                    item_name
                )
            # Price (optional structure)
            price_el = ET.SubElement(il, ET.QName(nsmap["cac"], "Price"))
            ET.SubElement(price_el, ET.QName(nsmap["cbc"], "PriceAmount")).text = (
                f"{price:.2f}"
            )

    # Tax total (optional)
    if total_tax_amt > 0:
        tax_total = ET.SubElement(root, ET.QName(nsmap["cac"], "TaxTotal"))
        ET.SubElement(tax_total, ET.QName(nsmap["cbc"], "TaxAmount")).text = (
            f"{total_tax_amt:.2f}"
        )

    # LegalMonetaryTotal (optional minimal)
    if line_total > 0:
        lmt = ET.SubElement(root, ET.QName(nsmap["cac"], "LegalMonetaryTotal"))
        ET.SubElement(lmt, ET.QName(nsmap["cbc"], "LineExtensionAmount")).text = (
            f"{line_total:.2f}"
        )
        ET.SubElement(lmt, ET.QName(nsmap["cbc"], "TaxExclusiveAmount")).text = (
            f"{line_total:.2f}"
        )
        ET.SubElement(lmt, ET.QName(nsmap["cbc"], "TaxInclusiveAmount")).text = (
            f"{(line_total + total_tax_amt):.2f}"
        )

    # Add a lightweight note carrying payload size for traceability
    note = ET.SubElement(root, ET.QName(nsmap["cbc"], "Note"))
    note.text = f"payload:{len(str(payload or {}))}B"

    return ET.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=False)


def validate_xml_against_xsd(
    xml_bytes: bytes, schemas_dir: str | None = None
) -> List[str]:
    """
    Validate the given XML against UBL 2.1 Invoice XSD if available under schemas_dir.
    - Expects main XSD at: {schemas_dir}/maindoc/UBL-Invoice-2.1.xsd
    - If schemas are missing, returns [] (non-fatal, validation skipped).
    """
    if not schemas_dir:
        return []
    import os

    main_xsd = os.path.join(schemas_dir, "maindoc", "UBL-Invoice-2.1.xsd")
    if not os.path.isfile(main_xsd):
        return []  # silently skip when no schemas available

    try:
        # nosec: B320
        xml_doc = ET.fromstring(xml_bytes)
        with open(main_xsd, "rb") as f:
            # nosec: B320
            xsd_doc = ET.parse(f)
        schema = ET.XMLSchema(xsd_doc)
        schema.assertValid(xml_doc)
        return []
    except ET.DocumentInvalid:  # schema validation errors
        # Return lines of error log
        return [str(err) for err in schema.error_log]  # type: ignore[name-defined]
    except (
        Exception
    ) as e:  # Parsing or IO problems – surface as generic single error line
        return [f"Validation error: {e}"]
