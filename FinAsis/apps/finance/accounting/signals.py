from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction
from datetime import date

from .models import Voucher, VoucherLine, GLBalance
from decimal import Decimal

@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"[Signal] Yeni kullanıcı oluşturuldu: {instance.username}")
        # Burada kullanıcı oluşturulduğunda yapılacak işlemleri ekleyebilirsiniz.
        # Örneğin, kullanıcıya varsayılan bir profil oluşturma işlemi yapılabilir.


@receiver(post_save, sender=Voucher)
def update_gl_balances_on_post(sender, instance: Voucher, created, **kwargs):
    """Fiş kaydedildiğinde (state='posted') GL özetlerini güncelle.

    Basit yaklaşım: Fiş her kaydedildiğinde ilgili ay için debit/credit toplamlarına ekle ve end_balance'ı yeniden hesapla.
    """
    # Sadece posted olanlar işlenir
    if instance.state != 'posted':
        return

    voucher_month = instance.date.month
    voucher_year = instance.date.year
    company = instance.company
    currency = (instance.currency.code if getattr(instance, 'currency', None) else 'TRY')

    lines = VoucherLine.objects.filter(voucher=instance)
    # Atomik güncelleme
    with transaction.atomic():
        for line in lines:
            glb, _ = GLBalance.objects.select_for_update().get_or_create(
                company=company,
                fiscal_year=instance.fiscal_year,
                account=line.account,
                currency=currency,
                year=voucher_year,
                month=voucher_month,
                defaults={'begin_balance': Decimal('0.00')}
            )
            # Güncelle
            if line.debit_amount:
                glb.debit_total = (glb.debit_total or 0) + line.debit_amount
            if line.credit_amount:
                glb.credit_total = (glb.credit_total or 0) + line.credit_amount
            glb.end_balance = (glb.begin_balance or 0) + (glb.debit_total or 0) - (glb.credit_total or 0)
            glb.save()