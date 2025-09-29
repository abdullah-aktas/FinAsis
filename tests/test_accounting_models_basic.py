import pytest
from django.utils import timezone
from src.apps.accounting.models import Company, Customer, Invoice, Expense, Product, Sale, Payment

@pytest.mark.django_db
def test_company_create_and_read():
    c = Company.objects.create(name="Test AŞ", tax_number="1234567890")
    assert c.pk is not None
    fetched = Company.objects.get(pk=c.pk)
    assert fetched.name == "Test AŞ"

@pytest.mark.django_db
def test_invoice_with_gib_fields_nullable():
    company = Company.objects.create(name="Firm", tax_number="1234567890")
    customer = Customer.objects.create(company=company, first_name="Ali", last_name="Veli")
    inv = Invoice.objects.create(
        company=company,
        customer=customer,
        invoice_number="INV-001",
        issue_date=timezone.now().date(),
        total_amount=100,
    )
    assert inv.gib_uuid is None
    assert inv.gib_status is None
    inv.gib_uuid = "abc123"
    inv.save()
    assert Invoice.objects.get(pk=inv.pk).gib_uuid == "abc123"

@pytest.mark.django_db
def test_sale_and_payment_flow():
    company = Company.objects.create(name="Flow", tax_number="1234567890")
    customer = Customer.objects.create(company=company, first_name="Ayşe", last_name="Demir")
    product = Product.objects.create(company=company, name="Ürün", price=50, stock=10)
    sale = Sale.objects.create(company=company, customer=customer, product=product, quantity=2, unit_price=50)
    assert sale.total_price == 100
    pay = Payment.objects.create(company=company, customer=customer, amount=100, payment_method='NAKIT')
    assert pay.amount == 100

@pytest.mark.django_db
def test_expense_categories_constant_integrity():
    company = Company.objects.create(name="Const", tax_number="1234567890")
    exp = Expense.objects.create(company=company, category='KIRA', amount=1000, expense_date=timezone.now().date())
    assert exp.category == 'KIRA'
