from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Invoice, Payment, Expense, Customer, Vendor, Company
from .services.journal import create_invoice_entry, create_payment_entry
from common.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=Invoice)
def auto_journal_invoice(sender, instance, created, **kwargs):
    if created:
        try:
            create_invoice_entry(instance)
        except Exception:
            # Sessiz geç; ileride logging eklenebilir
            pass
        
        # Otomatik bildirim gönder
        try:
            # Faturayı oluşturan kullanıcıyı bul
            user = instance.created_by if hasattr(instance, 'created_by') and instance.created_by else None
            if not user and hasattr(instance, 'company') and instance.company:
                user = instance.company.created_by if hasattr(instance.company, 'created_by') else None
            
            if user:
                NotificationService.notify_invoice_created(instance, user)
            else:
                logger.warning(f"Fatura bildirimi gönderilemedi: Kullanıcı bulunamadı - Invoice #{instance.id}")
        except Exception as e:
            logger.error(f"Fatura bildirimi hatası: {e}")


@receiver(post_save, sender=Payment)
def auto_journal_payment(sender, instance, created, **kwargs):
    if created:
        try:
            create_payment_entry(instance)
        except Exception:
            pass
        
        # Otomatik bildirim gönder
        try:
            # Ödemeyi oluşturan kullanıcıyı bul
            user = instance.created_by if hasattr(instance, 'created_by') and instance.created_by else None
            if not user and hasattr(instance, 'invoice') and instance.invoice:
                user = instance.invoice.created_by if hasattr(instance.invoice, 'created_by') else None
            
            if user:
                NotificationService.notify_payment_received(instance, user)
            else:
                logger.warning(f"Ödeme bildirimi gönderilemedi: Kullanıcı bulunamadı - Payment #{instance.id}")
        except Exception as e:
            logger.error(f"Ödeme bildirimi hatası: {e}")


@receiver(post_save, sender=Expense)
def auto_notify_expense(sender, instance, created, **kwargs):
    """Gider oluşturulduğunda bildirim gönder"""
    if created:
        try:
            # Gideri oluşturan kullanıcıyı bul
            user = instance.created_by if hasattr(instance, 'created_by') and instance.created_by else None
            if not user and hasattr(instance, 'company') and instance.company:
                user = instance.company.created_by if hasattr(instance.company, 'created_by') else None
            
            if user:
                NotificationService.notify_expense_created(instance, user)
            else:
                logger.warning(f"Gider bildirimi gönderilemedi: Kullanıcı bulunamadı - Expense #{instance.id}")
        except Exception as e:
            logger.error(f"Gider bildirimi hatası: {e}")


@receiver(post_save, sender=Customer)
def auto_notify_customer_added(sender, instance, created, **kwargs):
    """Müşteri eklendiğinde bildirim gönder"""
    if created:
        try:
            # Müşteriyi ekleyen kullanıcıyı bul
            user = instance.created_by if hasattr(instance, 'created_by') and instance.created_by else None
            if not user and hasattr(instance, 'company') and instance.company:
                user = instance.company.created_by if hasattr(instance.company, 'created_by') else None
            
            if user:
                NotificationService.notify_customer_added(instance, user)
        except Exception as e:
            logger.error(f"Müşteri bildirimi hatası: {e}")


@receiver(post_save, sender=Vendor)
def auto_notify_vendor_added(sender, instance, created, **kwargs):
    """Tedarikçi eklendiğinde bildirim gönder"""
    if created:
        try:
            # Tedarikçiyi ekleyen kullanıcıyı bul
            user = instance.created_by if hasattr(instance, 'created_by') and instance.created_by else None
            if not user and hasattr(instance, 'company') and instance.company:
                user = instance.company.created_by if hasattr(instance.company, 'created_by') else None
            
            if user:
                title = "👥 Yeni Tedarikçi Eklendi"
                message = f"{instance.name} tedarikçisi başarıyla eklendi."
                action_url = f"/accounting/vendor/{instance.id}/" if hasattr(instance, 'id') else "/accounting/vendors/"
                
                NotificationService.send_notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type="success",
                    priority="low",
                    action_url=action_url,
                    category="vendor",
                    module="accounting",
                    send_email=False,
                )
        except Exception as e:
            logger.error(f"Tedarikçi bildirimi hatası: {e}")


@receiver(post_save, sender=Company)
def auto_notify_company_updated(sender, instance, created, **kwargs):
    """Şirket bilgileri güncellendiğinde bildirim gönder"""
    if not created:  # Sadece güncellemeler için
        try:
            # Şirketi güncelleyen kullanıcıyı bul
            user = instance.updated_by if hasattr(instance, 'updated_by') and instance.updated_by else None
            if not user and hasattr(instance, 'created_by') and instance.created_by:
                user = instance.created_by
            
            if user:
                NotificationService.notify_company_updated(instance, user)
        except Exception as e:
            logger.error(f"Şirket bildirimi hatası: {e}")
