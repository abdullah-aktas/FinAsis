from __future__ import annotations
from typing import Optional, cast
from django.db.models import QuerySet
from .models import (
    Invoice,
    Expense,
    BankTransaction,
    Company,
    Customer,
    Payment,
    InvoiceQuerySet,
    ExpenseQuerySet,
    BankTransactionQuerySet,
    CustomerQuerySet,
    PaymentQuerySet,
)


def invoices_for_company(company: Optional[Company]) -> QuerySet[Invoice]:
    if not company:
        return Invoice.objects.none()
    qs = cast(InvoiceQuerySet, Invoice.objects)
    return qs.with_related().filter(company=company)


def expenses_for_company(company: Optional[Company]) -> QuerySet[Expense]:
    if not company:
        return Expense.objects.none()
    qs = cast(ExpenseQuerySet, Expense.objects)
    return qs.with_company().filter(company=company)


def banktransactions_for_company(
    company: Optional[Company],
) -> QuerySet[BankTransaction]:
    if not company:
        return BankTransaction.objects.none()
    qs = cast(BankTransactionQuerySet, BankTransaction.objects)
    return qs.with_related().filter(account__company=company)


def customers_for_company(company: Optional[Company]) -> QuerySet[Customer]:
    if not company:
        return Customer.objects.none()
    qs = cast(CustomerQuerySet, Customer.objects)
    return qs.with_company().filter(company=company)


def payments_for_company(company: Optional[Company]) -> QuerySet[Payment]:
    if not company:
        return Payment.objects.none()
    qs = cast(PaymentQuerySet, Payment.objects)
    return qs.with_related().filter(company=company)
