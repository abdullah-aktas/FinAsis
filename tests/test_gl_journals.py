import pytest
from decimal import Decimal
from django.utils import timezone
from src.apps.accounting.models import Company, Customer, Invoice, GLJournalEntry, ExchangeRate, Payment
from src.apps.accounting.services.journal import create_invoice_entry, create_payment_entry


@pytest.mark.django_db
def test_invoice_journal_double_entry():
    company = Company.objects.create(name='TestCo', country='TR', base_currency='TRY')
    customer = Customer.objects.create(company=company, first_name='Cust', last_name='Test')
    invoice = Invoice.objects.create(company=company, customer=customer, invoice_number='INV1', issue_date=timezone.now().date(), due_date=timezone.now().date(), currency='TRY', total_amount=Decimal('118.00'))
    # optional kdv_rate attribute if model lacks
    if not hasattr(invoice, 'kdv_rate'):
        invoice.kdv_rate = Decimal('0.18')
    create_invoice_entry(invoice)
    je = GLJournalEntry.objects.get(source_type='INVOICE', source_id=str(invoice.id))  # type: ignore[attr-defined]
    assert je.total_debit == je.total_credit == Decimal('118.00')
    lines = list(je.lines.all())  # type: ignore[attr-defined]
    # Expect 3 lines: AR debit, revenue credit, VAT credit
    assert len(lines) == 3
    ar = next(l for l in lines if l.account.code == '120')
    rev = next(l for l in lines if l.account.code == '600')
    vat = next(l for l in lines if l.account.code == '391')
    assert ar.debit == Decimal('118.00') and ar.credit == 0
    assert rev.credit + vat.credit == Decimal('118.00')


@pytest.mark.django_db
def test_payment_journal_double_entry():
    company = Company.objects.create(name='TestCo2', country='TR', base_currency='TRY')
    customer = Customer.objects.create(company=company, first_name='Cust', last_name='Test')
    payment = Payment.objects.create(company=company, customer=customer, amount=Decimal('50.00'), payment_method='NAKIT')
    create_payment_entry(payment)
    je = GLJournalEntry.objects.get(source_type='PAYMENT', source_id=str(payment.id))  # type: ignore[attr-defined]
    assert je.total_debit == je.total_credit == Decimal('50.00')
    lines = list(je.lines.all())  # type: ignore[attr-defined]
    assert len(lines) == 2
    cash = next(l for l in lines if l.account.code == '100')
    ar = next(l for l in lines if l.account.code == '120')
    assert cash.debit == Decimal('50.00') and cash.credit == 0
    assert ar.credit == Decimal('50.00') and ar.debit == 0


@pytest.mark.django_db
def test_fx_rate_and_amount_base():
    company = Company.objects.create(name='FXCo', country='TR', base_currency='TRY')
    # create FX rate USD -> TRY 30
    ExchangeRate.objects.create(base_currency='USD', quote_currency='TRY', date=timezone.now().date(), rate=Decimal('30'))
    customer = Customer.objects.create(company=company, first_name='FX', last_name='Cust')
    invoice = Invoice.objects.create(company=company, customer=customer, invoice_number='INVFX', issue_date=timezone.now().date(), due_date=timezone.now().date(), currency='USD', total_amount=Decimal('100.00'))
    if not hasattr(invoice, 'kdv_rate'):
        invoice.kdv_rate = Decimal('0.20')
    create_invoice_entry(invoice)
    je = GLJournalEntry.objects.get(source_type='INVOICE', source_id=str(invoice.id))  # type: ignore[attr-defined]
    assert je.total_debit == je.total_credit == Decimal('100.00')
    # Check amount_base conversion on one line
    line = je.lines.first()  # type: ignore[attr-defined]
    assert line.amount_base == (line.debit or line.credit) * line.fx_rate
    assert line.fx_rate == Decimal('30')
