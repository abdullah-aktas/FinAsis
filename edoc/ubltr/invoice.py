from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Optional

try:
    from lxml import etree  # type: ignore
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as etree  # type: ignore

from ..shared.config import EdocSettings
from .namespaces import UBL_NS


@dataclass(slots=True)
class Party:
    name: str
    tax_id: str


@dataclass(slots=True)
class Line:
    description: str
    quantity: Decimal
    unit_price: Decimal

    @property
    def line_extension_amount(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))


@dataclass(slots=True)
class TaxSubtotal:
    taxable_amount: Decimal
    tax_amount: Decimal
    percent: Optional[Decimal] = None  # e.g., 20 for %20
    tax_scheme_name: str = "KDV"


@dataclass(slots=True)
class TaxTotal:
    tax_amount: Decimal
    subtotals: List[TaxSubtotal] = field(default_factory=list)


@dataclass(slots=True)
class AllowanceCharge:
    charge_indicator: bool  # False: discount, True: charge
    amount: Decimal
    reason: Optional[str] = None


@dataclass(slots=True)
class PaymentMeans:
    code: str = "42"  # generic
    payment_due_date: Optional[date] = None
    payee_iban: Optional[str] = None


@dataclass(slots=True)
class Withholding:
    tax_amount: Decimal
    taxable_amount: Optional[Decimal] = None
    reason: Optional[str] = None


@dataclass(slots=True)
class Invoice:
    id: str
    issue_date: date
    supplier: Party
    customer: Party
    currency: str = "TRY"
    lines: List[Line] = field(default_factory=list)
    profile_id: str = "TICARIFATURA"
    customization_id: str = "TR1.2"
    tax_total: Optional[TaxTotal] = None
    allowance_charges: List[AllowanceCharge] = field(default_factory=list)
    payment_means: Optional[PaymentMeans] = None
    withholding_tax_total: Optional[Withholding] = None
    notes: List[str] = field(default_factory=list)  # e-Arşiv notları veya genel notlar

    def to_xml(self, settings: EdocSettings | None = None) -> etree._Element:
        """Build minimal UBL-TR 2.3 Invoice XML."""
        settings = settings or EdocSettings()
        # ElementTree doesn't support nsmap; build with lxml if available, else fallback.
        try:
            nsmap = {k or None: v for k, v in UBL_NS.items()}
            root = etree.Element("Invoice", nsmap=nsmap)  # type: ignore[call-arg]
        except TypeError:
            # Fallback: use namespaced tags with prefixes omitted (may render ns0:Invoice)
            root = etree.Element("Invoice")

        def cbc(tag: str, text: str) -> etree._Element:
            el = etree.SubElement(root, f"{{{UBL_NS['cbc']}}}{tag}")
            el.text = text
            return el

        def cac(parent: etree._Element, tag: str) -> etree._Element:
            return etree.SubElement(parent, f"{{{UBL_NS['cac']}}}{tag}")

        cbc("ProfileID", settings.profile_id or self.profile_id)
        cbc("CustomizationID", settings.customization_id or self.customization_id)
        cbc("ID", self.id)
        cbc("IssueDate", self.issue_date.isoformat())
        cbc("DocumentCurrencyCode", self.currency)

        # Notes (e-Arşiv açıklamaları vb.)
        for n in self.notes:
            cbc("Note", n)

        # Supplier
        acct = etree.SubElement(root, f"{{{UBL_NS['cac']}}}AccountingSupplierParty")
        party = cac(acct, "Party")
        party_name = cac(party, "PartyName")
        cbc_el = etree.SubElement(party_name, f"{{{UBL_NS['cbc']}}}Name")
        cbc_el.text = self.supplier.name
        tax = cac(party, "PartyTaxScheme")
        tax_id_el = etree.SubElement(tax, f"{{{UBL_NS['cbc']}}}CompanyID")
        tax_id_el.text = self.supplier.tax_id

        # Customer
        acct = etree.SubElement(root, f"{{{UBL_NS['cac']}}}AccountingCustomerParty")
        party = cac(acct, "Party")
        party_name = cac(party, "PartyName")
        cbc_el = etree.SubElement(party_name, f"{{{UBL_NS['cbc']}}}Name")
        cbc_el.text = self.customer.name
        tax = cac(party, "PartyTaxScheme")
        tax_id_el = etree.SubElement(tax, f"{{{UBL_NS['cbc']}}}CompanyID")
        tax_id_el.text = self.customer.tax_id

        # Lines
        base_total = Decimal("0.00")
        for i, line in enumerate(self.lines, start=1):
            il = etree.SubElement(root, f"{{{UBL_NS['cac']}}}InvoiceLine")
            lext = line.line_extension_amount
            base_total += lext

            el = etree.SubElement(il, f"{{{UBL_NS['cbc']}}}ID")
            el.text = str(i)
            qty = etree.SubElement(il, f"{{{UBL_NS['cbc']}}}InvoicedQuantity")
            qty.text = str(line.quantity)
            price = cac(il, "Price")
            price_amount = etree.SubElement(
                price, f"{{{UBL_NS['cbc']}}}PriceAmount", currencyID=self.currency
            )
            price_amount.text = f"{line.unit_price:.2f}"
            le = etree.SubElement(
                il, f"{{{UBL_NS['cbc']}}}LineExtensionAmount", currencyID=self.currency
            )
            le.text = f"{lext:.2f}"
            item = cac(il, "Item")
            desc = etree.SubElement(item, f"{{{UBL_NS['cbc']}}}Description")
            desc.text = line.description

        # Document Allowance/Charge
        for ac in self.allowance_charges:
            ac_el = cac(root, "AllowanceCharge")
            el = etree.SubElement(ac_el, f"{{{UBL_NS['cbc']}}}ChargeIndicator")
            el.text = "true" if ac.charge_indicator else "false"
            amt = etree.SubElement(
                ac_el, f"{{{UBL_NS['cbc']}}}Amount", currencyID=self.currency
            )
            amt.text = f"{ac.amount:.2f}"
            if ac.reason:
                r = etree.SubElement(ac_el, f"{{{UBL_NS['cbc']}}}AllowanceChargeReason")
                r.text = ac.reason

        # TaxTotal
        tax_amount_total = Decimal("0.00")
        if self.tax_total is not None:
            tax_amount_total = self.tax_total.tax_amount
            tt = cac(root, "TaxTotal")
            tamt = etree.SubElement(
                tt, f"{{{UBL_NS['cbc']}}}TaxAmount", currencyID=self.currency
            )
            tamt.text = f"{self.tax_total.tax_amount:.2f}"
            for st in self.tax_total.subtotals:
                sub = cac(tt, "TaxSubtotal")
                txb = etree.SubElement(
                    sub, f"{{{UBL_NS['cbc']}}}TaxableAmount", currencyID=self.currency
                )
                txb.text = f"{st.taxable_amount:.2f}"
                txa = etree.SubElement(
                    sub, f"{{{UBL_NS['cbc']}}}TaxAmount", currencyID=self.currency
                )
                txa.text = f"{st.tax_amount:.2f}"
                if st.percent is not None:
                    perc = etree.SubElement(sub, f"{{{UBL_NS['cbc']}}}Percent")
                    perc.text = f"{st.percent:.2f}"
                cat = cac(sub, "TaxCategory")
                scheme = cac(cat, "TaxScheme")
                name = etree.SubElement(scheme, f"{{{UBL_NS['cbc']}}}Name")
                name.text = st.tax_scheme_name

        # Withholding (Tevkifat)
        withholding_amount = Decimal("0.00")
        if self.withholding_tax_total is not None:
            w = cac(root, "WithholdingTaxTotal")
            wamt = etree.SubElement(
                w, f"{{{UBL_NS['cbc']}}}TaxAmount", currencyID=self.currency
            )
            wamt.text = f"{self.withholding_tax_total.tax_amount:.2f}"
            withholding_amount = self.withholding_tax_total.tax_amount
            if self.withholding_tax_total.taxable_amount is not None:
                sub = cac(w, "TaxSubtotal")
                txb = etree.SubElement(
                    sub, f"{{{UBL_NS['cbc']}}}TaxableAmount", currencyID=self.currency
                )
                txb.text = f"{self.withholding_tax_total.taxable_amount:.2f}"
                txa = etree.SubElement(
                    sub, f"{{{UBL_NS['cbc']}}}TaxAmount", currencyID=self.currency
                )
                txa.text = f"{self.withholding_tax_total.tax_amount:.2f}"

        # PaymentMeans
        if self.payment_means is not None:
            pm = cac(root, "PaymentMeans")
            code = etree.SubElement(pm, f"{{{UBL_NS['cbc']}}}PaymentMeansCode")
            code.text = self.payment_means.code
            if self.payment_means.payment_due_date is not None:
                dd = etree.SubElement(pm, f"{{{UBL_NS['cbc']}}}PaymentDueDate")
                dd.text = self.payment_means.payment_due_date.isoformat()
            if self.payment_means.payee_iban:
                pa = cac(pm, "PayeeFinancialAccount")
                id_el = etree.SubElement(pa, f"{{{UBL_NS['cbc']}}}ID")
                id_el.text = self.payment_means.payee_iban

        # Compute payable: base_total +/- allowances + tax - withholding
        total_after_allowances = base_total
        for ac in self.allowance_charges:
            total_after_allowances = (
                total_after_allowances + ac.amount
                if ac.charge_indicator
                else total_after_allowances - ac.amount
            )
        payable_total = (
            total_after_allowances + tax_amount_total - withholding_amount
        ).quantize(Decimal("0.01"))

        mtotal = cac(root, "LegalMonetaryTotal")
        payable = etree.SubElement(
            mtotal, f"{{{UBL_NS['cbc']}}}PayableAmount", currencyID=self.currency
        )
        payable.text = f"{payable_total:.2f}"
        return root

    def to_xml_bytes(
        self, settings: EdocSettings | None = None, pretty: bool = True
    ) -> bytes:
        root = self.to_xml(settings)
        try:
            return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=pretty)  # type: ignore[call-arg]
        except TypeError:
            return etree.tostring(root, encoding="utf-8")
