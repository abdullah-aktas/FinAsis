from __future__ import annotations

from dataclasses import dataclass
from datetime import date

try:
    from lxml import etree  # type: ignore
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as etree  # type: ignore

from .namespaces import UBL_NS
from ..shared.config import EdocSettings
from .schema import validate_dispatch_xml


@dataclass(slots=True)
class DispatchParty:
    name: str


@dataclass(slots=True)
class Address:
    street: str | None = None
    city: str | None = None
    country: str | None = None


@dataclass(slots=True)
class DispatchLine:
    id: str
    item_name: str
    quantity: str | int | float
    unit_code: str = "C62"  # unit code default


@dataclass(slots=True)
class DispatchAdvice:
    id: str
    issue_date: date
    supplier: DispatchParty
    customer: DispatchParty
    delivery_address: Address | None = None
    lines: list[DispatchLine] | None = None

    def to_xml(self, settings: EdocSettings | None = None) -> etree._Element:
        settings = settings or EdocSettings()
        try:
            nsmap = {k or None: v for k, v in UBL_NS.items()}
            root = etree.Element("DispatchAdvice", nsmap=nsmap)  # type: ignore[call-arg]
        except TypeError:
            root = etree.Element("DispatchAdvice")

        def cbc(parent, tag, text):
            el = etree.SubElement(parent, f"{{{UBL_NS['cbc']}}}{tag}")
            el.text = text
            return el

        def cac(parent, tag):
            return etree.SubElement(parent, f"{{{UBL_NS['cac']}}}{tag}")

        cbc(root, "ID", self.id)
        cbc(root, "IssueDate", self.issue_date.isoformat())

        sp = cac(root, "DespatchSupplierParty")
        p = cac(sp, "Party")
        pn = cac(p, "PartyName")
        cbc(pn, "Name", self.supplier.name)

        cp = cac(root, "DeliveryCustomerParty")
        p2 = cac(cp, "Party")
        pn2 = cac(p2, "PartyName")
        cbc(pn2, "Name", self.customer.name)

        if self.delivery_address:
            da = cac(root, "Delivery")
            addr = cac(da, "DeliveryAddress")
            if self.delivery_address.street:
                cbc(addr, "StreetName", self.delivery_address.street)
            if self.delivery_address.city:
                cbc(addr, "CityName", self.delivery_address.city)
            if self.delivery_address.country:
                cbc(addr, "Country", self.delivery_address.country)

        if self.lines:
            for line in self.lines:
                ln = cac(root, "DespatchLine")
                cbc(ln, "ID", line.id)
                qty = etree.SubElement(ln, f"{{{UBL_NS['cbc']}}}DeliveredQuantity")
                qty.text = str(line.quantity)
                qty.set("unitCode", line.unit_code)
                item = cac(ln, "Item")
                cbc(item, "Name", line.item_name)

        return root

    def to_xml_bytes(
        self, settings: EdocSettings | None = None, pretty: bool = True
    ) -> bytes:
        root = self.to_xml(settings)
        try:
            return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=pretty)  # type: ignore[call-arg]
        except TypeError:
            return etree.tostring(root, encoding="utf-8")

    def validate(self, settings: EdocSettings | None = None) -> None:
        xml = self.to_xml_bytes(settings)
        validate_dispatch_xml(xml, settings)
