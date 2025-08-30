# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    Account, Transaction, Budget,
    FinancialReport, Tax
)

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

@receiver(pre_save, sender=Account)
def account_pre_save(sender, instance, **kwargs):
    """Hesap kaydetme öncesi işlemler"""
    if not instance.pk:  # Yeni kayıt
        # Hesap kodu kontrolü
        if not instance.code:
            raise ValueError(_('Hesap kodu zorunludur'))
        
        # Hesap kodu benzersizlik kontrolü
        if Account.objects.filter(code=instance.code).exists():
            raise ValueError(_('Bu hesap kodu zaten kullanılıyor'))

@receiver(post_save, sender=Transaction)
def transaction_post_save(sender, instance, created, **kwargs):
    """İşlem kaydetme sonrası işlemler"""
    if created:
        # İşlem durumu kontrolü
        if instance.status == 'POSTED':
            # Hesap bakiyesini güncelle
            account = instance.account
            if instance.type == 'DEBIT':
                account.balance += instance.amount
            else:
                account.balance -= instance.amount
            account.save()

@receiver(pre_save, sender=Budget)
def budget_pre_save(sender, instance, **kwargs):
    """Bütçe kaydetme öncesi işlemler"""
    if not instance.pk:  # Yeni kayıt
        # Tarih kontrolü
        if instance.start_date >= instance.end_date:
            raise ValueError(_('Başlangıç tarihi bitiş tarihinden önce olmalıdır'))
        
        # Bütçe tutarı kontrolü
        if instance.amount <= 0:
            raise ValueError(_('Bütçe tutarı pozitif olmalıdır'))

@receiver(post_save, sender=FinancialReport)
def financial_report_post_save(sender, instance, created, **kwargs):
    """Finansal rapor kaydetme sonrası işlemler"""
    if created:
        # Rapor durumu kontrolü
        if instance.status == 'GENERATED':
            # Rapor parametrelerini güncelle
            instance.parameters = {
                'generated_at': timezone.now().isoformat(),
                'generated_by': instance.created_by.username if instance.created_by else None
            }
            instance.save()

@receiver(pre_save, sender=Tax)
def tax_pre_save(sender, instance, **kwargs):
    """Vergi kaydetme öncesi işlemler"""
    if not instance.pk:  # Yeni kayıt
        # Vergi kodu kontrolü
        if not instance.code:
            raise ValueError(_('Vergi kodu zorunludur'))
        
        # Vergi kodu benzersizlik kontrolü
        if Tax.objects.filter(code=instance.code).exists():
            raise ValueError(_('Bu vergi kodu zaten kullanılıyor'))
        
        # Vergi oranı kontrolü
        if instance.rate < 0 or instance.rate > 100:
            raise ValueError(_('Vergi oranı 0 ile 100 arasında olmalıdır'))

@receiver(pre_delete, sender=Account)
def account_pre_delete(sender, instance, **kwargs):
    """Hesap silme öncesi işlemler"""
    # İlişkili işlemlerin kontrolü
    if instance.transactions.exists():
        raise ValueError(_('Bu hesaba ait işlemler bulunmaktadır. Önce işlemleri silmelisiniz'))

@receiver(pre_delete, sender=Transaction)
def transaction_pre_delete(sender, instance, **kwargs):
    """İşlem silme öncesi işlemler"""
    # İşlem durumu kontrolü
    if instance.status == 'POSTED':
        raise ValueError(_('Kaydedilmiş işlemler silinemez'))

@receiver(pre_delete, sender=Budget)
def budget_pre_delete(sender, instance, **kwargs):
    """Bütçe silme öncesi işlemler"""
    # Bütçe durumu kontrolü
    if instance.is_active:
        raise ValueError(_('Aktif bütçeler silinemez'))

@receiver(pre_delete, sender=FinancialReport)
def financial_report_pre_delete(sender, instance, **kwargs):
    """Finansal rapor silme öncesi işlemler"""
    # Rapor durumu kontrolü
    if instance.status == 'APPROVED':
        raise ValueError(_('Onaylanmış raporlar silinemez'))

@receiver(pre_delete, sender=Tax)
def tax_pre_delete(sender, instance, **kwargs):
    """Vergi silme öncesi işlemler"""
    # Vergi durumu kontrolü
    if instance.is_active:
        raise ValueError(_('Aktif vergiler silinemez')) 