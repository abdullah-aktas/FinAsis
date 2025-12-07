from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Optional

from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.barcode import qr as qrmod
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from .ubltr.invoice import Invoice


def generate_invoice_pdf(inv: Invoice, title: Optional[str] = None) -> bytes:
    """Render a minimal invoice PDF using reportlab.

    This is a simple, dependency-light renderer for e-Arşiv test PDFs.
    It doesn't attempt to be a full UBL visualizer but covers key fields.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, height - 20 * mm, title or "e-Arşiv Fatura")

    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, height - 28 * mm, f"Fatura No: {inv.id}")
    c.drawString(20 * mm, height - 34 * mm, f"Tarih: {inv.issue_date.isoformat()}")

    # Parties
    y = height - 48 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "Satıcı")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y - 6 * mm, f"Unvan: {inv.supplier.name}")
    c.drawString(20 * mm, y - 12 * mm, f"VKN/TCKN: {inv.supplier.tax_id}")

    y -= 22 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "Alıcı")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y - 6 * mm, f"Unvan: {inv.customer.name}")
    c.drawString(20 * mm, y - 12 * mm, f"VKN/TCKN: {inv.customer.tax_id}")

    # Lines header
    y -= 22 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Açıklama")
    c.drawRightString(150 * mm, y, "Miktar")
    c.drawRightString(180 * mm, y, f"Birim Fiyat ({inv.currency})")
    c.drawRightString(200 * mm, y, f"Tutar ({inv.currency})")

    y -= 6 * mm
    c.setLineWidth(0.3)
    c.line(20 * mm, y, 200 * mm, y)

    # Lines
    c.setFont("Helvetica", 10)
    y -= 6 * mm
    total = 0.0
    for ln in inv.lines:
        if y < 30 * mm:
            c.showPage()
            y = height - 20 * mm
        line_total = float(ln.line_extension_amount)
        total += line_total
        c.drawString(20 * mm, y, ln.description[:60])
        c.drawRightString(150 * mm, y, f"{ln.quantity}")
        c.drawRightString(180 * mm, y, f"{ln.unit_price:.2f}")
        c.drawRightString(200 * mm, y, f"{line_total:.2f}")
        y -= 6 * mm

    # Totals
    y -= 6 * mm
    c.line(120 * mm, y, 200 * mm, y)
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(180 * mm, y, "Toplam:")
    c.drawRightString(200 * mm, y, f"{total:.2f} {inv.currency}")

    # Notes
    if inv.notes:
        y -= 14 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, "Notlar")
        c.setFont("Helvetica", 9)
        for note in inv.notes:
            y -= 5 * mm
            c.drawString(20 * mm, y, f"- {note}")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawRightString(200 * mm, 10 * mm, f"Oluşturma: {datetime.utcnow().isoformat()}Z")

    c.showPage()
    c.save()
    return buffer.getvalue()


def _format_money(v: Decimal | float) -> str:
    try:
        if isinstance(v, Decimal):
            return f"{v:.2f}"
    except Exception:
        pass
    return f"{float(v):.2f}"


def generate_invoice_pdf_corporate(
    inv: Invoice,
    *,
    logo_path: Optional[str] = None,
    add_qr: bool = True,
    qr_text: Optional[str] = None,
    title: Optional[str] = "FATURA",
) -> bytes:
    """Corporate-styled invoice PDF with logo, table grid, tax/discount details and QR.

    - Draws logo (if provided), supplier and customer blocks
    - Line items in a bordered table
    - Totals with allowance/charges and tax breakdown
    - Optional QR code with basic invoice fingerprint
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    margin_l, margin_r, margin_t, margin_b = 15 * mm, 15 * mm, 18 * mm, 18 * mm
    y = height - margin_t

    # Header: Logo and Title
    if logo_path:
        try:
            c.drawImage(
                logo_path,
                margin_l,
                y - 14 * mm,
                width=30 * mm,
                height=14 * mm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width - margin_r, y - 6 * mm, title or "FATURA")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin_r, y - 12 * mm, f"No: {inv.id}")
    c.drawRightString(
        width - margin_r, y - 17 * mm, f"Tarih: {inv.issue_date.isoformat()}"
    )
    y -= 22 * mm

    # Supplier and Customer boxes
    box_h = 28 * mm
    box_w = (width - margin_l - margin_r - 6 * mm) / 2
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    # Supplier
    c.rect(margin_l, y - box_h, box_w, box_h, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_l + 4 * mm, y - 6 * mm, "Satıcı")
    c.setFont("Helvetica", 9)
    c.drawString(margin_l + 4 * mm, y - 12 * mm, f"Unvan: {inv.supplier.name}")
    c.drawString(margin_l + 4 * mm, y - 18 * mm, f"VKN/TCKN: {inv.supplier.tax_id}")

    # Customer
    cx = margin_l + box_w + 6 * mm
    c.rect(cx, y - box_h, box_w, box_h, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(cx + 4 * mm, y - 6 * mm, "Alıcı")
    c.setFont("Helvetica", 9)
    c.drawString(cx + 4 * mm, y - 12 * mm, f"Unvan: {inv.customer.name}")
    c.drawString(cx + 4 * mm, y - 18 * mm, f"VKN/TCKN: {inv.customer.tax_id}")

    y -= box_h + 10 * mm

    # Items table
    col_x = [
        margin_l,
        margin_l + 80 * mm,
        margin_l + 105 * mm,
        margin_l + 135 * mm,
        margin_l + 165 * mm,
        width - margin_r,
    ]
    headers = [
        "Açıklama",
        "Miktar",
        "Birim",
        f"Birim Fiyat ({inv.currency})",
        f"Tutar ({inv.currency})",
    ]
    # Table header
    c.setFont("Helvetica-Bold", 9)
    c.line(margin_l, y, width - margin_r, y)
    y -= 6 * mm
    c.drawString(col_x[0] + 2, y, headers[0])
    c.drawRightString(col_x[2] - 2, y, headers[1])
    c.drawRightString(col_x[3] - 2, y, headers[3])
    c.drawRightString(col_x[4] - 2, y, headers[4])
    y -= 3 * mm
    c.line(margin_l, y, width - margin_r, y)
    y -= 4 * mm

    c.setFont("Helvetica", 9)
    line_height = 6 * mm
    base_total = Decimal("0.00")

    def ensure_page_break(current_y: float) -> float:
        if current_y < margin_b + 60 * mm:
            c.showPage()
            # re-establish page context
            c.setFont("Helvetica", 9)
            return height - margin_t
        return current_y

    for ln in inv.lines:
        y = ensure_page_break(y)
        desc = ln.description
        qty = str(ln.quantity)
        unit_price = _format_money(ln.unit_price)
        line_total = ln.line_extension_amount
        base_total += line_total

        # Description truncate to fit
        max_desc_width = col_x[1] - col_x[0] - 6
        if stringWidth(desc, "Helvetica", 9) > max_desc_width:
            while (
                stringWidth(desc + "…", "Helvetica", 9) > max_desc_width
                and len(desc) > 3
            ):
                desc = desc[:-1]
            desc += "…"

        c.drawString(col_x[0] + 2, y, desc)
        c.drawRightString(col_x[2] - 2, y, qty)
        c.drawRightString(col_x[3] - 2, y, unit_price)
        c.drawRightString(col_x[4] - 2, y, _format_money(line_total))
        # row line
        y -= line_height
        c.setStrokeColor(colors.lightgrey)
        c.line(margin_l, y + 2, width - margin_r, y + 2)
        c.setStrokeColor(colors.black)

    # Totals box
    y -= 6 * mm
    totals_w = 70 * mm
    tx = width - margin_r - totals_w
    box_h2 = 40 * mm
    c.rect(tx, y - box_h2, totals_w, box_h2, stroke=1, fill=0)

    # Compute totals similar to XML builder
    total_after_allowances = base_total
    total_discount = Decimal("0.00")
    total_charge = Decimal("0.00")
    for ac in inv.allowance_charges:
        if ac.charge_indicator:
            total_after_allowances += ac.amount
            total_charge += ac.amount
        else:
            total_after_allowances -= ac.amount
            total_discount += ac.amount
    tax_amount_total = inv.tax_total.tax_amount if inv.tax_total else Decimal("0.00")
    payable_total = (
        total_after_allowances
        + tax_amount_total
        - (
            inv.withholding_tax_total.tax_amount
            if inv.withholding_tax_total
            else Decimal("0.00")
        )
    )

    ty = y - 6 * mm
    c.setFont("Helvetica", 9)

    def label_row(name: str, val: str):
        nonlocal ty
        c.drawString(tx + 4 * mm, ty, name)
        c.drawRightString(tx + totals_w - 4 * mm, ty, val)
        ty -= 5 * mm

    label_row("Ara Toplam:", f"{_format_money(base_total)} {inv.currency}")
    if total_discount > 0:
        label_row("İskonto:", f"-{_format_money(total_discount)} {inv.currency}")
    if total_charge > 0:
        label_row("Masraf/Ek:", f"+{_format_money(total_charge)} {inv.currency}")
    if inv.tax_total and inv.tax_total.subtotals:
        for st in inv.tax_total.subtotals:
            perc = f" %{st.percent}" if st.percent is not None else ""
            label_row(
                f"{st.tax_scheme_name}{perc}:",
                f"{_format_money(st.tax_amount)} {inv.currency}",
            )
    else:
        label_row("Vergi:", f"{_format_money(tax_amount_total)} {inv.currency}")
    c.setFont("Helvetica-Bold", 10)
    label_row("Genel Toplam:", f"{_format_money(payable_total)} {inv.currency}")

    # Notes
    if inv.notes:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin_l, y - 6 * mm, "Notlar")
        c.setFont("Helvetica", 8)
        ny = y - 11 * mm
        for note in inv.notes:
            c.drawString(margin_l, ny, f"- {note}")
            ny -= 4.5 * mm

    # QR code (top-right of totals box)
    if add_qr:
        try:
            payload = (
                qr_text
                or f"INV:{inv.id}|DATE:{inv.issue_date.isoformat()}|SUP:{inv.supplier.tax_id}|TOT:{_format_money(payable_total)} {inv.currency}"
            )
            w = qrmod.QrCodeWidget(payload)
            b = 22 * mm
            d = Drawing(b, b)
            d.add(w)
            renderPDF.draw(d, c, tx - (b + 6 * mm), y - 2 * mm)
        except Exception:
            pass

    # Footer
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.grey)
    c.drawRightString(
        width - margin_r, margin_b - 4, f"Oluşturma: {datetime.utcnow().isoformat()}Z"
    )
    c.setFillColor(colors.black)

    c.showPage()
    c.save()
    return buf.getvalue()
