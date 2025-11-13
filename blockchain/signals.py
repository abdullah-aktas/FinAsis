from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from finance.accounting.models import Invoice
from accounting.models import EDefter
from .services import ensure_record, payload_for_invoice, payload_for_edefter, payload_for_voucher, payload_for_payment, payload_for_expense, payload_for_banktxn
from finance.accounting.models import Voucher, VoucherLine
from accounting.models import Payment, Expense, BankTransaction


@receiver(post_save, sender=Invoice)
def hash_invoice(sender, instance: Invoice, created, **kwargs):
    payload = payload_for_invoice(instance)
    ensure_record(reference=f"invoice:{instance.id}", payload=payload, status='anchored' if getattr(instance, 'gib_uuid', None) else 'pending')


@receiver(post_save, sender=EDefter)
def hash_edefter(sender, instance: EDefter, created, **kwargs):
    payload = payload_for_edefter(instance)
    ensure_record(reference=f"edefter:{instance.id}", payload=payload, status='anchored' if instance.status in ['gonderildi', 'onayli', 'approved'] else 'pending')


@receiver(post_save, sender=Voucher)
def hash_voucher(sender, instance: Voucher, created, **kwargs):
    lines = VoucherLine.objects.filter(voucher=instance).order_by('line_no')
    payload = payload_for_voucher(instance, lines)
    ensure_record(reference=f"voucher:{instance.id}", payload=payload, status='anchored' if instance.state == 'posted' else 'pending')


@receiver(post_save, sender=Payment)
def hash_payment(sender, instance: Payment, created, **kwargs):
    payload = payload_for_payment(instance)
    ensure_record(reference=f"payment:{instance.id}", payload=payload, status='anchored')


@receiver(post_save, sender=Expense)
def hash_expense(sender, instance: Expense, created, **kwargs):
    payload = payload_for_expense(instance)
    ensure_record(reference=f"expense:{instance.id}", payload=payload, status='anchored')


@receiver(post_save, sender=BankTransaction)
def hash_bank_transaction(sender, instance: BankTransaction, created, **kwargs):
    payload = payload_for_banktxn(instance)
    ensure_record(reference=f"banktxn:{instance.id}", payload=payload, status='anchored')

