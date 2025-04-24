from datetime import datetime, timedelta
from decimal import Decimal
from django.db import models
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class TurkishTaxCalculator:
    def __init__(self):
        self.current_year = timezone.now().year
        self.kdv_rates = {
            'standard': Decimal('0.20'),  # %20
            'reduced': Decimal('0.10'),   # %10
            'special': Decimal('0.01'),   # %1
            'zero': Decimal('0.00')       # %0
        }
        
    def calculate_kdv(self, amount, rate_type='standard'):
        """
        KDV hesaplama
        """
        try:
            rate = self.kdv_rates.get(rate_type, self.kdv_rates['standard'])
            kdv_amount = amount * rate
            return {
                'net_amount': amount,
                'kdv_rate': rate,
                'kdv_amount': kdv_amount,
                'total_amount': amount + kdv_amount
            }
        except Exception as e:
            logger.error(f"KDV hesaplama hatası: {str(e)}")
            raise

    def calculate_stopaj(self, amount, stopaj_type='standard'):
        """
        Stopaj hesaplama
        """
        stopaj_rates = {
            'standard': Decimal('0.20'),  # %20
            'reduced': Decimal('0.10'),   # %10
            'special': Decimal('0.05')    # %5
        }
        
        try:
            rate = stopaj_rates.get(stopaj_type, stopaj_rates['standard'])
            stopaj_amount = amount * rate
            return {
                'gross_amount': amount,
                'stopaj_rate': rate,
                'stopaj_amount': stopaj_amount,
                'net_amount': amount - stopaj_amount
            }
        except Exception as e:
            logger.error(f"Stopaj hesaplama hatası: {str(e)}")
            raise

    def calculate_gecikme_zammi(self, amount, due_date):
        """
        Gecikme zammı hesaplama
        """
        try:
            today = timezone.now().date()
            if today <= due_date:
                return Decimal('0.00')
            
            days_late = (today - due_date).days
            monthly_rate = Decimal('0.0367')  # %3.67 aylık gecikme zammı oranı
            
            gecikme_zammi = amount * (monthly_rate * Decimal(days_late / 30))
            return gecikme_zammi
        except Exception as e:
            logger.error(f"Gecikme zammı hesaplama hatası: {str(e)}")
            raise

    def calculate_tevkifat(self, amount, tevkifat_type='standard'):
        """
        Tevkifat hesaplama
        """
        tevkifat_rates = {
            'standard': Decimal('0.20'),  # %20
            'reduced': Decimal('0.10'),   # %10
            'special': Decimal('0.05')    # %5
        }
        
        try:
            rate = tevkifat_rates.get(tevkifat_type, tevkifat_rates['standard'])
            tevkifat_amount = amount * rate
            return {
                'gross_amount': amount,
                'tevkifat_rate': rate,
                'tevkifat_amount': tevkifat_amount,
                'net_amount': amount - tevkifat_amount
            }
        except Exception as e:
            logger.error(f"Tevkifat hesaplama hatası: {str(e)}")
            raise

class TurkishAccountingRules:
    def __init__(self):
        self.current_period = timezone.now()
        
    def get_fiscal_year(self):
        """
        Mali yıl hesaplama
        """
        current_month = self.current_period.month
        if current_month >= 1 and current_month <= 12:
            return self.current_period.year
        return self.current_period.year + 1

    def get_accounting_period(self):
        """
        Muhasebe dönemi hesaplama
        """
        fiscal_year = self.get_fiscal_year()
        return {
            'start_date': datetime(fiscal_year, 1, 1),
            'end_date': datetime(fiscal_year, 12, 31)
        }

    def calculate_depreciation(self, asset_value, useful_life, method='straight_line'):
        """
        Amortisman hesaplama
        """
        try:
            if method == 'straight_line':
                annual_depreciation = asset_value / useful_life
                return {
                    'annual_depreciation': annual_depreciation,
                    'monthly_depreciation': annual_depreciation / 12
                }
            else:
                raise ValueError("Desteklenmeyen amortisman metodu")
        except Exception as e:
            logger.error(f"Amortisman hesaplama hatası: {str(e)}")
            raise

class TurkishTaxReporting:
    def __init__(self):
        self.tax_calculator = TurkishTaxCalculator()
        self.accounting_rules = TurkishAccountingRules()
        self.current_period = timezone.now()
        
    def generate_monthly_vat_report(self, transactions):
        """
        Aylık KDV raporu oluşturma
        """
        try:
            report = {
                'period': self.current_period.strftime('%Y-%m'),
                'transactions': [],
                'totals': {
                    'total_sales': Decimal('0.00'),
                    'total_purchases': Decimal('0.00'),
                    'total_kdv_collected': Decimal('0.00'),
                    'total_kdv_paid': Decimal('0.00'),
                    'net_kdv': Decimal('0.00')
                }
            }
            
            for transaction in transactions:
                kdv_calculation = self.tax_calculator.calculate_kdv(
                    transaction['amount'],
                    transaction.get('kdv_rate_type', 'standard')
                )
                
                report['transactions'].append({
                    'date': transaction['date'],
                    'description': transaction['description'],
                    'amount': transaction['amount'],
                    'kdv_amount': kdv_calculation['kdv_amount'],
                    'type': transaction['type']
                })
                
                if transaction['type'] == 'sale':
                    report['totals']['total_sales'] += transaction['amount']
                    report['totals']['total_kdv_collected'] += kdv_calculation['kdv_amount']
                else:
                    report['totals']['total_purchases'] += transaction['amount']
                    report['totals']['total_kdv_paid'] += kdv_calculation['kdv_amount']
            
            report['totals']['net_kdv'] = (
                report['totals']['total_kdv_collected'] -
                report['totals']['total_kdv_paid']
            )
            
            return report
        except Exception as e:
            logger.error(f"KDV raporu oluşturma hatası: {str(e)}")
            raise 