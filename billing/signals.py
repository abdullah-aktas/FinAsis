from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone
import logging

from .models import SubscriptionProfile, Transaction, Invoice

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def ensure_billing_profile(sender, instance, created, **kwargs):
    if created:
        try:
            SubscriptionProfile.objects.get_or_create(user=instance)
        except (OperationalError, ProgrammingError):
            # Tablo henüz yoksa (migrasyon uygulanmamışsa) sessizce geç
            pass


@receiver(post_save, sender=SubscriptionProfile)
def notify_subscription_changes(sender, instance, created, **kwargs):
    """Abonelik değişikliklerinde bildirim gönder"""
    try:
        from common.services.notification_service import NotificationService

        if created:
            # Yeni abonelik aktifleştirildi
            if instance.status == "active":
                NotificationService.notify_subscription_activated(
                    instance, instance.user
                )
        else:
            # Abonelik durumu değişti
            # Abonelik süresi dolmak üzere kontrolü
            if hasattr(instance, "end_date") and instance.end_date:
                days_remaining = (instance.end_date - timezone.now()).days
                if 0 < days_remaining <= 7:
                    NotificationService.notify_subscription_expiring(
                        instance, instance.user, days_remaining
                    )

            # Abonelik iptal edildi veya süresi doldu
            if instance.status in ["canceled", "past_due"]:
                title = "⚠️ Aboneliğiniz Sonlandı"
                message = f"Aboneliğiniz {instance.status} durumuna geçti.\n\n"
                message += "Hizmetlerinize kesintisiz devam etmek için aboneliğinizi yenileyin."

                NotificationService.send_notification(
                    user=instance.user,
                    title=title,
                    message=message,
                    notification_type="warning",
                    priority="high",
                    action_url="/billing/portal/",
                    category="subscription",
                    module="billing",
                    send_email=True,
                )

    except Exception as e:
        logger.error(f"Abonelik bildirimi hatası: {e}")


@receiver(post_save, sender=Transaction)
def handle_payment_confirmation(sender, instance, created, **kwargs):
    """Ödeme onaylandığında blockchain sözleşme oluştur ve bildirim gönder"""
    # Sadece ödeme tamamlandığında işlem yap
    if instance.status != "completed":
        return

    try:
        from billing.services.blockchain_contract import SubscriptionBlockchainService
        from billing.services.notification_service import BillingNotificationService

        # Abonelik profili al
        subscription_profile = SubscriptionProfile.objects.filter(
            user=instance.user
        ).first()

        if not subscription_profile:
            logger.warning(
                f"Transaction {instance.id} için abonelik profili bulunamadı"
            )
            return

        # Fatura oluştur (varsa)
        invoice = None
        try:
            invoice = Invoice.objects.filter(
                subscription=subscription_profile, transaction=instance
            ).first()
        except Exception:
            pass

        # Blockchain sözleşme oluştur (10.000₺+ veya beta üye ise)
        contract_result = SubscriptionBlockchainService.create_subscription_contract(
            subscription_profile, transaction=instance
        )

        # Sözleşme bildirimi gönder
        if contract_result and contract_result.get("contract"):
            BillingNotificationService.send_contract_notification(
                instance.user, contract_result["contract"]
            )

        # Ödeme onayı bildirimi ve mail gönder
        BillingNotificationService.send_payment_confirmation(
            subscription_profile, instance, invoice
        )

        # Fatura e-postası gönder (varsa)
        if invoice:
            BillingNotificationService.send_invoice_email(instance.user, invoice)

        logger.info(
            f"Ödeme onayı işlemleri tamamlandı: Transaction {instance.id}, "
            f"User {instance.user.username}"
        )

    except Exception as e:
        logger.error(f"Ödeme onayı işlem hatası: {e}", exc_info=True)


@receiver(post_save, sender=Invoice)
def handle_invoice_created(sender, instance, created, **kwargs):
    """Fatura oluşturulduğunda otomatik gönder"""
    if created and instance.status == "SENT":
        try:
            from billing.services.notification_service import BillingNotificationService

            BillingNotificationService.send_invoice_email(
                instance.subscription.user, instance
            )

            logger.info(
                f"Fatura e-postası gönderildi: Invoice {instance.invoice_number}"
            )

        except Exception as e:
            logger.error(f"Fatura e-postası gönderme hatası: {e}", exc_info=True)
