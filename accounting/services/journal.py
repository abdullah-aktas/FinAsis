from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from ..models import (
    GLJournalEntry,
    GLJournalLine,
    GLAccount,
    Invoice,
    Payment,
    ExchangeRate,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # Hinting to static analyzers
    # Django automatically adds 'id' primary key; explicit for linters
    class _Invoice(Invoice):  # type: ignore
        id: int

    class _Payment(Payment):  # type: ignore
        id: int


VAT_ACCOUNT_CODE = "391"
REVENUE_ACCOUNT_CODE = "600"
AR_ACCOUNT_CODE = "120"
CASH_ACCOUNT_CODE = "100"


def get_account(company, code, name_fallback, category):
    acc, _ = GLAccount.objects.get_or_create(
        company=company,
        code=code,
        defaults={
            "name": name_fallback,
            "category": category,
            "currency": company.base_currency,
        },
    )
    return acc


def fx_rate(base_currency: str, tx_currency: str, date):
    if base_currency == tx_currency:
        return Decimal("1")
    rate = ExchangeRate.objects.filter(
        base_currency=tx_currency, quote_currency=base_currency, date=date
    ).first()
    if rate:
        return rate.rate
    # Basit fallback: 1 (uyarı üretilebilir)
    return Decimal("1")


def round2(v):
    return (
        (v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        if isinstance(v, Decimal)
        else Decimal(v).quantize(Decimal("0.01"))
    )


@transaction.atomic
def create_invoice_entry(invoice: Invoice):
    """Satış faturası için yevmiye (BRUT satış + KDV + Alacak Hesabı)."""
    inv_id = getattr(invoice, "id", None)
    if GLJournalEntry.objects.filter(
        company=invoice.company, source_type="INVOICE", source_id=inv_id
    ).exists():
        return
    company = invoice.company
    number = f"INV-{invoice.invoice_number}"
    je = GLJournalEntry.objects.create(
        company=company,
        number=number,
        date=invoice.issue_date,
        description=f"Fatura {invoice.invoice_number}",
        source_type="INVOICE",
        source_id=str(inv_id),
        currency=invoice.currency,
    )
    rate = fx_rate(company.base_currency, invoice.currency, invoice.issue_date)
    # Hesaplar
    ar = get_account(company, AR_ACCOUNT_CODE, "Alıcılar", "ASSET")
    revenue = get_account(company, REVENUE_ACCOUNT_CODE, "Satış Geliri", "INCOME")
    vat = get_account(company, VAT_ACCOUNT_CODE, "Hesaplanan KDV", "LIAB")
    total = Decimal(invoice.total_amount)
    kdv_oran = (
        Decimal(invoice.kdv_rate) if hasattr(invoice, "kdv_rate") else Decimal("0.20")
    )
    net = (total / (Decimal("1") + kdv_oran)).quantize(Decimal("0.01"))
    kdv = total - net
    # Borç: 120 Alıcılar
    GLJournalLine.objects.create(
        entry=je,
        account=ar,
        debit=total,
        credit=0,
        currency=invoice.currency,
        fx_rate=rate,
    )
    # Alacak: 600 Satış Geliri
    GLJournalLine.objects.create(
        entry=je,
        account=revenue,
        debit=0,
        credit=net,
        currency=invoice.currency,
        fx_rate=rate,
    )
    # Alacak: 391 Hesaplanan KDV
    if kdv > 0:
        GLJournalLine.objects.create(
            entry=je,
            account=vat,
            debit=0,
            credit=kdv,
            currency=invoice.currency,
            fx_rate=rate,
        )
    je.recalc_totals()
    return je


@transaction.atomic
def create_payment_entry(payment: Payment):
    pay_id = getattr(payment, "id", None)
    if GLJournalEntry.objects.filter(
        company=payment.company, source_type="PAYMENT", source_id=pay_id
    ).exists():
        return
    company = payment.company
    number = f"PAY-{pay_id}"
    je = GLJournalEntry.objects.create(
        company=company,
        number=number,
        date=payment.payment_date,
        description=f"Ödeme {pay_id}",
        source_type="PAYMENT",
        source_id=str(pay_id),
        currency=payment.company.base_currency,
    )
    rate = fx_rate(
        company.base_currency, payment.company.base_currency, payment.payment_date
    )
    cash = get_account(company, CASH_ACCOUNT_CODE, "Kasa", "ASSET")
    ar = get_account(company, AR_ACCOUNT_CODE, "Alıcılar", "ASSET")
    amount = Decimal(payment.amount)
    GLJournalLine.objects.create(
        entry=je,
        account=cash,
        debit=amount,
        credit=0,
        currency=company.base_currency,
        fx_rate=rate,
    )
    GLJournalLine.objects.create(
        entry=je,
        account=ar,
        debit=0,
        credit=amount,
        currency=company.base_currency,
        fx_rate=rate,
    )
    je.recalc_totals()
    return je
