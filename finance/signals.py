from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction, CashFlow

@receiver(post_save, sender=Transaction)
def update_cash_flow_on_transaction_save(sender, instance, created, **kwargs):
    """
    Bir işlem kaydedildiğinde ilgili nakit akışı kaydını günceller.
    """
    if created:
        # Yeni işlem için nakit akışı kaydı oluştur veya güncelle
        cash_flow, _ = CashFlow.objects.get_or_create(
            period='daily',
            start_date=instance.date,
            end_date=instance.date,
            defaults={
                'opening_balance': 0,
                'closing_balance': 0,
                'total_income': 0,
                'total_expense': 0,
                'net_cash_flow': 0,
                'currency': instance.currency,
                'virtual_company': instance.virtual_company,
            }
        )
        
        # İşlem tipine göre nakit akışını güncelle
        if instance.transaction_type == 'income':
            cash_flow.total_income += instance.amount
            cash_flow.net_cash_flow += instance.amount
        elif instance.transaction_type == 'expense':
            cash_flow.total_expense += instance.amount
            cash_flow.net_cash_flow -= instance.amount
            
        cash_flow.closing_balance = cash_flow.opening_balance + cash_flow.net_cash_flow
        cash_flow.save()

@receiver(post_delete, sender=Transaction)
def update_cash_flow_on_transaction_delete(sender, instance, **kwargs):
    """
    Bir işlem silindiğinde ilgili nakit akışı kaydını günceller.
    """
    try:
        cash_flow = CashFlow.objects.get(
            period='daily',
            start_date=instance.date,
            end_date=instance.date,
            currency=instance.currency,
            virtual_company=instance.virtual_company,
        )
        
        # İşlem tipine göre nakit akışını güncelle
        if instance.transaction_type == 'income':
            cash_flow.total_income -= instance.amount
            cash_flow.net_cash_flow -= instance.amount
        elif instance.transaction_type == 'expense':
            cash_flow.total_expense -= instance.amount
            cash_flow.net_cash_flow += instance.amount
            
        cash_flow.closing_balance = cash_flow.opening_balance + cash_flow.net_cash_flow
        cash_flow.save()
    except CashFlow.DoesNotExist:
        pass  # Nakit akışı kaydı bulunamadıysa bir şey yapma 