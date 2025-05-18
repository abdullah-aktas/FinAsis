from decimal import Decimal
from django.db import transaction, models
from django.db.models import Sum
from django.utils import timezone
from .models import Account, Invoice, Transaction, CashFlow

class AccountingManager:
    def __init__(self):
        self.current_period = timezone.now()

    def create_account(self, **kwargs):
        """Yeni hesap oluştur"""
        return Account.objects.create(**kwargs)

    def create_invoice(self, **kwargs):
        """Yeni fatura oluştur"""
        return Invoice.objects.create(**kwargs)

    def create_transaction(self, **kwargs):
        """Yeni işlem oluştur"""
        return Transaction.objects.create(**kwargs)

    def get_account_balance(self, account_id, start_date=None, end_date=None):
        """Hesap bakiyesi sorgula"""
        account = Account.objects.get(id=account_id)
        balance = account.get_balance(start_date, end_date)
        return balance

    @transaction.atomic 
    def record_transaction(self, **kwargs):
        """Muhasebe işlemi kaydet"""
        trans = Transaction.objects.create(**kwargs)
        
        # Nakit akışı kaydı
        CashFlow.objects.create(
            date=trans.date,
            type='inflow' if trans.amount > 0 else 'outflow',
            amount=abs(trans.amount),
            category=trans.type,
            description=trans.description
        )
        
        return trans

    def get_period_totals(self, start_date, end_date):
        """Dönem toplamlarını hesapla"""
        totals = Transaction.objects.filter(
            date__range=(start_date, end_date)
        ).aggregate(
            total_debit=Sum('debit_amount'),
            total_credit=Sum('credit_amount')
        )
        return {
            'total_debit': totals['total_debit'] or Decimal('0'),
            'total_credit': totals['total_credit'] or Decimal('0')
        }
