"""
Banka entegrasyonları için test dosyası.
"""
import pytest
from django.test import TestCase
from apps.integrations.bank_integration.models import BankAccount, BankTransaction
from unittest.mock import patch, MagicMock

class BankAccountModelTest(TestCase):
    """Banka hesap modeli testleri."""
    
    def setUp(self):
        self.bank_account = BankAccount.objects.create(
            name="Test Hesabı",
            account_number="TR123456789012345678901234",
            currency="TRY"
        )
    
    def test_bank_account_creation(self):
        """Banka hesabı oluşturma testi."""
        self.assertEqual(self.bank_account.name, "Test Hesabı")
        self.assertEqual(self.bank_account.account_number, "TR123456789012345678901234")
        self.assertEqual(self.bank_account.currency, "TRY")

class BankTransactionTest(TestCase):
    """Banka işlemleri testleri."""
    
    def setUp(self):
        self.bank_account = BankAccount.objects.create(
            name="Test Hesabı",
            account_number="TR123456789012345678901234",
            currency="TRY"
        )
        
        self.transaction = BankTransaction.objects.create(
            account=self.bank_account,
            amount=1000,
            description="Test İşlemi"
        )
    
    def test_transaction_creation(self):
        """Banka işlemi oluşturma testi."""
        self.assertEqual(self.transaction.account, self.bank_account)
        self.assertEqual(self.transaction.amount, 1000)
        self.assertEqual(self.transaction.description, "Test İşlemi")

@pytest.mark.integration
class BankAPIIntegrationTest(TestCase):
    """Banka API entegrasyon testleri."""
    
    @patch('apps.integrations.bank_integration.services.BankAPIClient')
    def test_get_account_balance(self, mock_api_client):
        """Hesap bakiyesi alma testi."""
        mock_instance = MagicMock()
        mock_instance.get_balance.return_value = {"balance": 5000, "currency": "TRY"}
        mock_api_client.return_value = mock_instance
        
        # Banka API istemcisini kullanarak test işlemi
        from apps.integrations.bank_integration.services import get_account_balance
        balance_info = get_account_balance("TR123456789012345678901234")
        
        self.assertEqual(balance_info["balance"], 5000)
        self.assertEqual(balance_info["currency"], "TRY")
    
    @patch('apps.integrations.bank_integration.services.BankAPIClient')
    def test_transfer_money(self, mock_api_client):
        """Para transferi testi."""
        mock_instance = MagicMock()
        mock_instance.transfer.return_value = {"status": "success", "transaction_id": "12345"}
        mock_api_client.return_value = mock_instance
        
        # Banka API istemcisini kullanarak test işlemi
        from apps.integrations.bank_integration.services import transfer_money
        result = transfer_money(
            from_account="TR123456789012345678901234",
            to_account="TR987654321098765432109876",
            amount=1000,
            description="Test Transfer"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["transaction_id"], "12345") 