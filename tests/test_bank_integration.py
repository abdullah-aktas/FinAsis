"""
Banka entegrasyonları için test dosyası.
"""
import pytest
from django.test import TestCase
from integrations.bank_integration.models import BankAccount, BankTransaction
from unittest.mock import patch, MagicMock
from datetime import datetime
from decimal import Decimal

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
    
    @pytest.fixture
    def mock_bank_api(self):
        with patch('bank_integration.api.BankAPI') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_account_balance(self, mock_bank_api):
        mock_bank_api.get_balance.return_value = {
            'balance': Decimal('1000.00'),
            'currency': 'TRY',
            'last_updated': datetime.now()
        }
        
        from bank_integration.services import get_account_balance
        balance = get_account_balance('123456789')
        
        assert balance['balance'] == Decimal('1000.00')
        assert balance['currency'] == 'TRY'
        mock_bank_api.get_balance.assert_called_once_with('123456789')

    def test_transfer_money(self, mock_bank_api):
        mock_bank_api.transfer.return_value = {
            'transaction_id': 'TRX123',
            'status': 'completed',
            'amount': Decimal('500.00'),
            'fee': Decimal('5.00')
        }
        
        from bank_integration.services import transfer_money
        result = transfer_money(
            from_account='123456789',
            to_account='987654321',
            amount=Decimal('500.00')
        )
        
        assert result['status'] == 'completed'
        assert result['amount'] == Decimal('500.00')
        mock_bank_api.transfer.assert_called_once()

    def test_error_handling(self, mock_bank_api):
        mock_bank_api.get_balance.side_effect = Exception('API Error')
        
        from bank_integration.services import get_account_balance
        with pytest.raises(Exception) as exc_info:
            get_account_balance('123456789')
        
        assert str(exc_info.value) == 'API Error'

    def test_rate_limiting(self, mock_bank_api):
        from bank_integration.services import get_account_balance
        
        # 10 istek yap
        for _ in range(10):
            get_account_balance('123456789')
        
        # 11. istek rate limit'e takılmalı
        mock_bank_api.get_balance.side_effect = Exception('Rate limit exceeded')
        with pytest.raises(Exception) as exc_info:
            get_account_balance('123456789')
        
        assert str(exc_info.value) == 'Rate limit exceeded'

    def test_data_validation(self, mock_bank_api):
        from bank_integration.services import transfer_money
        
        with pytest.raises(ValueError):
            transfer_money(
                from_account='123',
                to_account='987654321',
                amount=Decimal('-100.00')
            )
        
        mock_bank_api.transfer.assert_not_called() 