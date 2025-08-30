from django.test import TestCase
from .models import Company, Customer, Invoice, Expense, BankAccount, BankTransaction
from datetime import date
from django.urls import reverse
from rest_framework.test import APIClient

class AccountingTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Şirketi", tax_number="1234567890")
        self.customer = Customer.objects.create(company=self.company, first_name="Ali", last_name="Veli")
        self.account = BankAccount.objects.create(company=self.company, bank_name="Test Bankası", iban="TR000000000000000000000000", account_name="Ali Veli", account_type="VADESIZ", balance=1000)

    def test_invoice_creation(self):
        invoice = Invoice.objects.create(company=self.company, customer=self.customer, invoice_number="FTR001", issue_date=date.today(), total_amount=500)
        self.assertEqual(invoice.total_amount, 500)
        self.assertEqual(invoice.company, self.company)

    def test_expense_creation(self):
        expense = Expense.objects.create(company=self.company, category="KIRA", amount=250, expense_date=date.today())
        self.assertEqual(expense.amount, 250)
        self.assertEqual(expense.category, "KIRA")

    def test_bank_transaction(self):
        tx = BankTransaction.objects.create(account=self.account, amount=200, transaction_type="IN")
        self.assertEqual(tx.amount, 200)
        self.assertEqual(tx.account, self.account)

class AccountingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.company = Company.objects.create(name="Test Şirketi", tax_number="1234567890")
        self.customer = Customer.objects.create(company=self.company, first_name="Ali", last_name="Veli")
        self.invoice = Invoice.objects.create(company=self.company, customer=self.customer, invoice_number="FTR001", issue_date=date.today(), total_amount=500)

    def test_company_list_api(self):
        url = reverse('accounting:api_companies-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Auth zorunlu

    def test_invoice_list_api(self):
        url = reverse('accounting:api_invoices-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Auth zorunlu

    def test_webhook_api(self):
        url = reverse('accounting:api_webhook')
        response = self.client.post(url, {'test': 'data'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('received', response.data)

    def test_ai_suggest_entry_api(self):
        url = reverse('accounting:api_ai_suggest_entry')
        response = self.client.post(url, {'context': {}}, format='json')
        self.assertEqual(response.status_code, 401)  # Auth zorunlu
