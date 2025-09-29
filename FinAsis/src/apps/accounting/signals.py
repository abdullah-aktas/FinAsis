from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Invoice, Payment
from .services.journal import create_invoice_entry, create_payment_entry

@receiver(post_save, sender=Invoice)
def auto_journal_invoice(sender, instance, created, **kwargs):
    if created:
        try:
            create_invoice_entry(instance)
        except Exception:
            # Sessiz geç; ileride logging eklenebilir
            pass

@receiver(post_save, sender=Payment)
def auto_journal_payment(sender, instance, created, **kwargs):
    if created:
        try:
            create_payment_entry(instance)
        except Exception:
            pass
