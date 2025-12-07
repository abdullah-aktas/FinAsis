# e-Fatura ile ilgili servis fonksiyonları burada tanımlanacak.

import requests
from django.conf import settings
from ..models import Invoice
import logging
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

efatura_logger = logging.getLogger("efatura")


def _pretty_xml(elem: Element) -> bytes:
    rough = tostring(elem, encoding="utf-8")
    # nosec: B318
    return minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")


def generate_invoice_xml(invoice: Invoice) -> bytes:
    """
    Minimal UBL-TR benzeri XML (MVP):
    Not: Gerçek UBL şemalarına uygun değil; test/demolar için yeterli.
    """
    inv = Element("Invoice")
    SubElement(inv, "ID").text = str(invoice.invoice_number)
    SubElement(inv, "IssueDate").text = invoice.issue_date.isoformat()
    if invoice.due_date:
        SubElement(inv, "DueDate").text = invoice.due_date.isoformat()
    SubElement(inv, "DocumentCurrencyCode").text = getattr(invoice, "currency", "TRY")

    acct = SubElement(inv, "AccountingSupplierParty")
    supplier = SubElement(acct, "Party")
    SubElement(supplier, "Name").text = (
        getattr(invoice.company, "name", "")
        if getattr(invoice, "company", None)
        else ""
    )
    SubElement(supplier, "TaxNumber").text = (
        getattr(invoice.company, "tax_number", "")
        if getattr(invoice, "company", None)
        else ""
    )

    cust = SubElement(inv, "AccountingCustomerParty")
    party = SubElement(cust, "Party")
    SubElement(party, "Name").text = str(invoice.customer)

    legal_monetary = SubElement(inv, "LegalMonetaryTotal")
    SubElement(legal_monetary, "PayableAmount").text = str(invoice.total_amount)

    lines = SubElement(inv, "InvoiceLines")
    try:
        items = invoice.items.all()
    except Exception:
        items = []
    if items:
        for it in items:
            line = SubElement(lines, "InvoiceLine")
            SubElement(line, "Description").text = (
                it.description or getattr(it.product, "name", "") or ""
            )
            SubElement(line, "Quantity").text = str(it.quantity)
            SubElement(line, "UnitPrice").text = str(it.unit_price)
            SubElement(line, "LineExtensionAmount").text = str(it.total_price)
    else:
        # Items yoksa tek satır toplam
        line = SubElement(lines, "InvoiceLine")
        SubElement(line, "Description").text = "Toplam"
        SubElement(line, "Quantity").text = "1"
        SubElement(line, "UnitPrice").text = str(invoice.total_amount)
        SubElement(line, "LineExtensionAmount").text = str(invoice.total_amount)

    tax_total = SubElement(inv, "TaxTotal")
    kdv_rate = getattr(invoice, "kdv_rate", None)
    if kdv_rate is not None:
        SubElement(tax_total, "TaxAmount").text = str(
            float(invoice.total_amount) * float(kdv_rate)
        )
        SubElement(tax_total, "TaxPercent").text = str(float(kdv_rate) * 100)

    return _pretty_xml(inv)


def send_invoice_to_gib(invoice: Invoice):
    xml_bytes = generate_invoice_xml(invoice)
    base_url = settings.GIB_EFATURA_BASE_URL
    # Basit e-Arşiv ayrımı: modelde e_archive alanı varsa kontrol et
    endpoint = (
        "sendEArchive"
        if hasattr(invoice, "e_archive") and getattr(invoice, "e_archive", False)
        else "sendInvoice"
    )
    url = f"{base_url}/{endpoint}"
    headers = {"Content-Type": "application/xml"}
    try:
        response = requests.post(
            url,
            data=xml_bytes,
            headers=headers,
            auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD),
            timeout=30,
        )
        invoice.gib_status = "sent" if response.status_code == 200 else "error"
        invoice.gib_response = response.text
        invoice.save()
        efatura_logger.info(
            f"Fatura {invoice.pk} GİB'e gönderildi. Status: {response.status_code}, Yanıt: {response.text}"
        )
        return response
    except Exception as e:
        efatura_logger.error(f"Fatura {invoice.pk} GİB gönderim hatası: {str(e)}")
        invoice.gib_status = "error"
        invoice.gib_response = str(e)
        invoice.save()
        raise


def check_invoice_status(invoice: Invoice):
    base_url = settings.GIB_EFATURA_BASE_URL
    endpoint = (
        "earchiveStatus"
        if hasattr(invoice, "e_archive") and getattr(invoice, "e_archive", False)
        else "invoiceStatus"
    )
    url = f"{base_url}/{endpoint}/{invoice.gib_uuid}"
    try:
        response = requests.get(
            url, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD), timeout=30
        )
        invoice.gib_status = response.json().get("status", "unknown")
        invoice.gib_response = response.text
        invoice.save()
        efatura_logger.info(
            f"Fatura {invoice.pk} GİB durum sorgu. Status: {response.status_code}, Yanıt: {response.text}"
        )
        return response
    except Exception as e:
        efatura_logger.error(f"Fatura {invoice.pk} GİB durum sorgu hatası: {str(e)}")
        invoice.gib_status = "error"
        invoice.gib_response = str(e)
        invoice.save()
        raise


def cancel_invoice_on_gib(invoice: Invoice):
    base_url = settings.GIB_EFATURA_BASE_URL
    url = f"{base_url}/cancelInvoice/{invoice.gib_uuid}"
    try:
        response = requests.post(
            url, auth=(settings.GIB_USERNAME, settings.GIB_PASSWORD), timeout=30
        )
        invoice.gib_status = "cancelled" if response.status_code == 200 else "error"
        invoice.gib_response = response.text
        invoice.save()
        efatura_logger.info(
            f"Fatura {invoice.pk} GİB iptal. Status: {response.status_code}, Yanıt: {response.text}"
        )
        return response
    except Exception as e:
        efatura_logger.error(f"Fatura {invoice.pk} GİB iptal hatası: {str(e)}")
        invoice.gib_status = "error"
        invoice.gib_response = str(e)
        invoice.save()
        raise
