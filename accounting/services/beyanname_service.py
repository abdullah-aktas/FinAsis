from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

"""
Basit KDV, Muhtasar ve BA/BS XML üretici fonksiyonları.
Gerçek hayatta Gelir İdaresi Başkanlığı (GİB) şemalarına uygun UBL-TR/özel XSD'ler kullanılmalıdır.
Bu fonksiyonlar MVP/test amaçlı örnek şematik XML üretir.
"""


def _prettify(xml_bytes: bytes) -> bytes:
    # nosec: B318 - Internal XML formatting, not parsing untrusted data
    return minidom.parseString(xml_bytes).toprettyxml(  # noqa: B318
        indent="  ", encoding="utf-8"
    )


def generate_kdv_xml(company, period: str) -> bytes:
    root = Element("KDVDeclaration")
    SubElement(root, "CompanyName").text = getattr(company, "name", "Company")
    SubElement(root, "TaxNumber").text = getattr(company, "tax_number", "") or ""
    SubElement(root, "Period").text = period  # YYYY-MM
    # Örnek kalemler
    items = SubElement(root, "Items")
    item = SubElement(items, "Item")
    SubElement(item, "Base").text = "10000.00"
    SubElement(item, "Rate").text = "20"
    SubElement(item, "Tax").text = "2000.00"
    return _prettify(tostring(root, encoding="utf-8"))


def generate_muhtasar_xml(company, period: str) -> bytes:
    root = Element("WithholdingDeclaration")
    SubElement(root, "CompanyName").text = getattr(company, "name", "Company")
    SubElement(root, "TaxNumber").text = getattr(company, "tax_number", "") or ""
    SubElement(root, "Period").text = period
    payroll = SubElement(root, "Payroll")
    row = SubElement(payroll, "Row")
    SubElement(row, "GrossWage").text = "5000.00"
    SubElement(row, "Withholding").text = "750.00"
    return _prettify(tostring(root, encoding="utf-8"))


def generate_babs_xml(company, period: str) -> bytes:
    root = Element("BABS")
    SubElement(root, "CompanyName").text = getattr(company, "name", "Company")
    SubElement(root, "TaxNumber").text = getattr(company, "tax_number", "") or ""
    SubElement(root, "Period").text = period
    purchases = SubElement(root, "Purchases")
    SubElement(purchases, "Total").text = "20000.00"
    sales = SubElement(root, "Sales")
    SubElement(sales, "Total").text = "15000.00"
    return _prettify(tostring(root, encoding="utf-8"))
