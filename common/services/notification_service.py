# -*- coding: utf-8 -*-
"""
Otomatik Bildirim Servisi
Kullanıcılara işlem bazlı otomatik bildirimler (in-app ve e-posta) gönderir
"""

import logging
from typing import Optional, List, Dict, Any
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from accounts.models import UserNotification
from common.tasks import send_email_async

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """Otomatik bildirim servisi - in-app ve e-posta bildirimleri"""
    
    @staticmethod
    def send_notification(
        user,
        title: str,
        message: str,
        notification_type: str = "info",
        priority: str = "normal",
        action_url: Optional[str] = None,
        category: Optional[str] = None,
        module: Optional[str] = None,
        send_email: bool = True,
        email_subject: Optional[str] = None,
        email_template: Optional[str] = None,
        **kwargs
    ) -> UserNotification:
        """
        Kullanıcıya bildirim gönderir (in-app + opsiyonel e-posta)
        
        Args:
            user: Kullanıcı nesnesi
            title: Bildirim başlığı
            message: Bildirim mesajı
            notification_type: info, success, warning, error, system
            priority: low, normal, high, urgent
            action_url: Tıklanabilir URL
            category: Bildirim kategorisi
            module: Modül adı
            send_email: E-posta gönderilsin mi?
            email_subject: E-posta başlığı (None ise title kullanılır)
            email_template: E-posta şablonu (gelecekte kullanılabilir)
        
        Returns:
            UserNotification: Oluşturulan bildirim nesnesi
        """
        try:
            # In-app bildirim oluştur
            notification = UserNotification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                action_url=action_url or "",
                category=category or "",
                module=module or "",
            )
            
            # E-posta gönder (kullanıcı tercihine göre)
            if send_email and user.email:
                try:
                    # Kullanıcı e-posta bildirimlerini kapatmış mı kontrol et
                    # (gelecekte UserPreference modeli eklenebilir)
                    email_subject = email_subject or title
                    
                    # E-posta içeriği oluştur
                    email_body = NotificationService._create_email_body(
                        user, title, message, action_url, notification_type
                    )
                    
                    # Async e-posta gönder
                    if hasattr(settings, 'CELERY_BROKER_URL') and settings.CELERY_BROKER_URL:
                        # Celery varsa async gönder
                        send_email_async.delay(
                            subject=email_subject,
                            message=email_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                        )
                    else:
                        # Celery yoksa sync gönder
                        send_mail(
                            subject=email_subject,
                            message=email_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=True,
                        )
                    
                    logger.info(f"E-posta bildirimi gönderildi: {user.email} - {title}")
                except Exception as e:
                    logger.warning(f"E-posta gönderilemedi: {e}")
            
            logger.info(f"Bildirim oluşturuldu: {user.username} - {title}")
            return notification
            
        except Exception as e:
            logger.error(f"Bildirim oluşturulamadı: {e}")
            raise
    
    @staticmethod
    def _create_email_body(
        user, title: str, message: str, action_url: Optional[str], notification_type: str
    ) -> str:
        """E-posta içeriği oluştur"""
        site_url = getattr(settings, 'SITE_URL', 'https://finasis.com.tr')
        
        # Bildirim tipine göre emoji
        emoji_map = {
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
            "system": "🔔",
        }
        emoji = emoji_map.get(notification_type, "📬")
        
        body = f"""
{emoji} {title}

{message}

"""
        
        if action_url:
            if action_url.startswith('/'):
                full_url = f"{site_url}{action_url}"
            else:
                full_url = action_url
            body += f"Detaylar için: {full_url}\n\n"
        
        body += f"""
---
FinAsis Platform
{site_url}

Bu bildirimi almak istemiyorsanız, hesap ayarlarınızdan bildirim tercihlerinizi değiştirebilirsiniz.
"""
        
        return body
    
    @staticmethod
    def notify_invoice_created(invoice, user):
        """Fatura oluşturulduğunda bildirim gönder"""
        title = "Yeni Fatura Oluşturuldu"
        message = f"Fatura #{invoice.invoice_number} başarıyla oluşturuldu.\n"
        message += f"Müşteri: {invoice.customer.name if invoice.customer else 'N/A'}\n"
        message += f"Tutar: {invoice.total_amount:,.2f} {invoice.currency}"
        
        action_url = reverse('accounting:invoice_detail', args=[invoice.id])
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            priority="normal",
            action_url=action_url,
            category="invoice",
            module="accounting",
            send_email=True,
        )
    
    @staticmethod
    def notify_payment_received(payment, user):
        """Ödeme alındığında bildirim gönder"""
        title = "Ödeme Alındı"
        message = f"Ödeme başarıyla kaydedildi.\n"
        message += f"Tutar: {payment.amount:,.2f} {payment.currency}\n"
        message += f"Tarih: {payment.payment_date.strftime('%d.%m.%Y')}"
        
        action_url = reverse('accounting:payment_detail', args=[payment.id]) if hasattr(payment, 'id') else ""
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            priority="normal",
            action_url=action_url,
            category="payment",
            module="accounting",
            send_email=True,
        )
    
    @staticmethod
    def notify_expense_created(expense, user):
        """Gider oluşturulduğunda bildirim gönder"""
        title = "Yeni Gider Kaydedildi"
        message = f"Gider başarıyla kaydedildi.\n"
        message += f"Kategori: {expense.category.name if hasattr(expense, 'category') and expense.category else 'N/A'}\n"
        message += f"Tutar: {expense.amount:,.2f} {expense.currency if hasattr(expense, 'currency') else 'TRY'}"
        
        action_url = reverse('accounting:expense_detail', args=[expense.id]) if hasattr(expense, 'id') else ""
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="info",
            priority="normal",
            action_url=action_url,
            category="expense",
            module="accounting",
            send_email=False,  # Giderler için e-posta gönderme (tercih edilebilir)
        )
    
    @staticmethod
    def notify_financial_report_generated(report, user):
        """Finansal rapor oluşturulduğunda bildirim gönder"""
        title = "Finansal Rapor Hazır"
        message = f"{report.report_type if hasattr(report, 'report_type') else 'Finansal'} raporu hazırlandı.\n"
        message += f"Tarih: {report.created_at.strftime('%d.%m.%Y %H:%M') if hasattr(report, 'created_at') else timezone.now().strftime('%d.%m.%Y %H:%M')}"
        
        action_url = reverse('finance:report_detail', args=[report.id]) if hasattr(report, 'id') else ""
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            priority="normal",
            action_url=action_url,
            category="report",
            module="finance",
            send_email=True,
        )
    
    @staticmethod
    def notify_low_balance(bank_account, user, threshold):
        """Banka hesabı düşük bakiye uyarısı"""
        title = "⚠️ Düşük Bakiye Uyarısı"
        message = f"{bank_account.name if hasattr(bank_account, 'name') else 'Banka Hesabı'} bakiyesi düşük.\n"
        message += f"Mevcut Bakiye: {bank_account.balance:,.2f} {bank_account.currency if hasattr(bank_account, 'currency') else 'TRY'}\n"
        message += f"Eşik Değer: {threshold:,.2f}"
        
        action_url = reverse('finance:bank_account_detail', args=[bank_account.id]) if hasattr(bank_account, 'id') else ""
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="high",
            action_url=action_url,
            category="balance",
            module="finance",
            send_email=True,
        )
    
    @staticmethod
    def notify_system_alert(user, title: str, message: str, priority: str = "high"):
        """Sistem uyarısı gönder"""
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="system",
            priority=priority,
            category="system",
            module="common",
            send_email=True,
        )
    
    # ============================================================================
    # KULLANICI HESAP İŞLEMLERİ
    # ============================================================================
    
    @staticmethod
    def notify_user_registered(user):
        """Kullanıcı kayıt olduğunda bildirim gönder"""
        title = "🎉 Hoş Geldiniz!"
        message = f"FinAsis'e hoş geldiniz {user.get_full_name() or user.username}!\n\n"
        message += "Hesabınız başarıyla oluşturuldu. Platformu kullanmaya başlayabilirsiniz.\n\n"
        message += "İlk adımlar:\n"
        message += "• Profil bilgilerinizi tamamlayın\n"
        message += "• Şirket bilgilerinizi ekleyin\n"
        message += "• Abonelik planınızı seçin"
        
        action_url = "/accounts/profile/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            priority="normal",
            action_url=action_url,
            category="account",
            module="accounts",
            send_email=True,
        )
    
    @staticmethod
    def notify_password_changed(user, ip_address: str = None):
        """Şifre değiştirildiğinde bildirim gönder"""
        title = "🔒 Şifre Değiştirildi"
        message = "Hesabınızın şifresi başarıyla değiştirildi.\n\n"
        if ip_address:
            message += f"İşlem IP adresi: {ip_address}\n"
        message += "\nEğer bu işlemi siz yapmadıysanız, lütfen hemen destek ekibimizle iletişime geçin."
        
        action_url = "/accounts/settings/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="high",
            action_url=action_url,
            category="security",
            module="accounts",
            send_email=True,
        )
    
    @staticmethod
    def notify_suspicious_login(user, ip_address: str, location: str = None):
        """Şüpheli giriş denemesi bildirimi"""
        title = "⚠️ Şüpheli Giriş Denemesi"
        message = f"Hesabınıza yeni bir cihazdan giriş yapıldı.\n\n"
        message += f"IP Adresi: {ip_address}\n"
        if location:
            message += f"Konum: {location}\n"
        message += "\nEğer bu siz değilseniz, lütfen hemen şifrenizi değiştirin."
        
        action_url = "/accounts/settings/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="high",
            action_url=action_url,
            category="security",
            module="accounts",
            send_email=True,
        )
    
    @staticmethod
    def notify_account_locked(user, reason: str = None):
        """Hesap kilitlendiğinde bildirim gönder"""
        title = "🔒 Hesap Kilitlendi"
        message = "Hesabınız güvenlik nedeniyle geçici olarak kilitlenmiştir.\n\n"
        if reason:
            message += f"Sebep: {reason}\n\n"
        message += "Hesabınızı açmak için destek ekibimizle iletişime geçin."
        
        action_url = "/support/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="error",
            priority="urgent",
            action_url=action_url,
            category="security",
            module="accounts",
            send_email=True,
        )
    
    # ============================================================================
    # ABONELİK VE FATURALAMA
    # ============================================================================
    
    @staticmethod
    def notify_subscription_activated(subscription, user):
        """Abonelik aktifleştirildiğinde bildirim gönder"""
        title = "✅ Aboneliğiniz Aktif"
        message = f"{subscription.plan.display_name if hasattr(subscription.plan, 'display_name') else subscription.plan.name} aboneliğiniz aktif edildi.\n\n"
        message += f"Başlangıç: {subscription.start_date.strftime('%d.%m.%Y') if hasattr(subscription, 'start_date') else 'N/A'}\n"
        message += f"Bitiş: {subscription.end_date.strftime('%d.%m.%Y') if hasattr(subscription, 'end_date') else 'N/A'}"
        
        action_url = "/billing/portal/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            priority="normal",
            action_url=action_url,
            category="subscription",
            module="billing",
            send_email=True,
        )
    
    @staticmethod
    def notify_subscription_expiring(subscription, user, days_remaining: int):
        """Abonelik süresi dolmadan önce bildirim gönder"""
        title = f"⏰ Aboneliğiniz {days_remaining} Gün İçinde Sona Eriyor"
        message = f"{subscription.plan.display_name if hasattr(subscription.plan, 'display_name') else subscription.plan.name} aboneliğiniz {days_remaining} gün içinde sona erecek.\n\n"
        message += "Kesintisiz hizmet için aboneliğinizi yenileyin."
        
        action_url = "/billing/portal/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="high",
            action_url=action_url,
            category="subscription",
            module="billing",
            send_email=True,
        )
    
    @staticmethod
    def notify_payment_successful(payment, user):
        """Ödeme başarılı olduğunda bildirim gönder"""
        title = "✅ Ödeme Başarılı"
        message = f"Ödemeniz başarıyla alındı.\n\n"
        message += f"Tutar: {payment.amount:,.2f} {payment.currency if hasattr(payment, 'currency') else 'TRY'}\n"
        message += f"Tarih: {payment.payment_date.strftime('%d.%m.%Y') if hasattr(payment, 'payment_date') else 'N/A'}"
        
        action_url = "/billing/invoices/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            priority="normal",
            action_url=action_url,
            category="payment",
            module="billing",
            send_email=True,
        )
    
    @staticmethod
    def notify_payment_failed(payment, user, reason: str = None):
        """Ödeme başarısız olduğunda bildirim gönder"""
        title = "❌ Ödeme Başarısız"
        message = f"Ödemeniz işleme alınamadı.\n\n"
        if reason:
            message += f"Sebep: {reason}\n\n"
        message += "Lütfen ödeme bilgilerinizi kontrol edin ve tekrar deneyin."
        
        action_url = "/billing/portal/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="error",
            priority="high",
            action_url=action_url,
            category="payment",
            module="billing",
            send_email=True,
        )
    
    # ============================================================================
    # HATIRLATMALAR VE UYARILAR
    # ============================================================================
    
    @staticmethod
    def notify_invoice_due_soon(invoice, user, days_until_due: int):
        """Fatura vadesi yaklaşıyor bildirimi"""
        title = f"📅 Fatura Vadesi {days_until_due} Gün Kaldı"
        message = f"Fatura #{invoice.invoice_number} için ödeme vadesi yaklaşıyor.\n\n"
        message += f"Tutar: {invoice.total_amount:,.2f} {invoice.currency}\n"
        message += f"Vade Tarihi: {invoice.due_date.strftime('%d.%m.%Y') if hasattr(invoice, 'due_date') and invoice.due_date else 'N/A'}"
        
        action_url = f"/accounting/invoice/{invoice.id}/" if hasattr(invoice, 'id') else "/accounting/invoices/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="normal",
            action_url=action_url,
            category="reminder",
            module="accounting",
            send_email=True,
        )
    
    @staticmethod
    def notify_invoice_overdue(invoice, user, days_overdue: int):
        """Fatura vadesi geçti bildirimi"""
        title = f"⚠️ Fatura Vadesi Geçti ({days_overdue} Gün)"
        message = f"Fatura #{invoice.invoice_number} için ödeme vadesi geçti.\n\n"
        message += f"Tutar: {invoice.total_amount:,.2f} {invoice.currency}\n"
        message += f"Vade Tarihi: {invoice.due_date.strftime('%d.%m.%Y') if hasattr(invoice, 'due_date') and invoice.due_date else 'N/A'}\n\n"
        message += "Lütfen ödemeyi en kısa sürede yapın."
        
        action_url = f"/accounting/invoice/{invoice.id}/" if hasattr(invoice, 'id') else "/accounting/invoices/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="error",
            priority="high",
            action_url=action_url,
            category="reminder",
            module="accounting",
            send_email=True,
        )
    
    @staticmethod
    def notify_low_stock(product, user, current_stock: int, min_stock: int):
        """Düşük stok uyarısı"""
        title = "📦 Düşük Stok Uyarısı"
        message = f"{product.name if hasattr(product, 'name') else 'Ürün'} için stok seviyesi düşük.\n\n"
        message += f"Mevcut Stok: {current_stock}\n"
        message += f"Minimum Stok: {min_stock}\n\n"
        message += "Lütfen stok takviyesi yapın."
        
        action_url = f"/accounting/product/{product.id}/" if hasattr(product, 'id') else "/accounting/products/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="normal",
            action_url=action_url,
            category="inventory",
            module="accounting",
            send_email=False,  # Stok uyarıları için e-posta opsiyonel
        )
    
    # ============================================================================
    # YETKİ VE ROL DEĞİŞİKLİKLERİ
    # ============================================================================
    
    @staticmethod
    def notify_role_changed(user, old_role: str, new_role: str):
        """Kullanıcı rolü değiştiğinde bildirim gönder"""
        title = "👤 Rolünüz Güncellendi"
        message = f"Hesabınızın rolü değiştirildi.\n\n"
        message += f"Eski Rol: {old_role}\n"
        message += f"Yeni Rol: {new_role}\n\n"
        message += "Yeni rolünüze göre erişim yetkileriniz güncellenmiştir."
        
        action_url = "/accounts/profile/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="info",
            priority="normal",
            action_url=action_url,
            category="role",
            module="accounts",
            send_email=True,
        )
    
    # ============================================================================
    # ŞİRKET VE MÜŞTERİ İŞLEMLERİ
    # ============================================================================
    
    @staticmethod
    def notify_company_updated(company, user):
        """Şirket bilgileri güncellendiğinde bildirim gönder"""
        title = "🏢 Şirket Bilgileri Güncellendi"
        message = f"{company.name} şirket bilgileri güncellendi.\n\n"
        message += "Değişiklikleri kontrol etmek için şirket sayfasını ziyaret edin."
        
        action_url = "/accounts/company/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="info",
            priority="low",
            action_url=action_url,
            category="company",
            module="accounts",
            send_email=False,
        )
    
    @staticmethod
    def notify_customer_added(customer, user):
        """Müşteri eklendiğinde bildirim gönder"""
        # Müşteri adını oluştur
        customer_name = ""
        if hasattr(customer, 'first_name') and hasattr(customer, 'last_name'):
            customer_name = f"{customer.first_name} {customer.last_name}".strip()
        elif hasattr(customer, 'name'):
            customer_name = customer.name
        else:
            customer_name = "Müşteri"
        
        title = "👥 Yeni Müşteri Eklendi"
        message = f"{customer_name} başarıyla eklendi."
        
        action_url = f"/accounting/customer/{customer.id}/" if hasattr(customer, 'id') else "/accounting/customers/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            priority="low",
            action_url=action_url,
            category="customer",
            module="accounting",
            send_email=False,
        )
    
    # ============================================================================
    # SİSTEM VE GÜVENLİK
    # ============================================================================
    
    @staticmethod
    def notify_security_incident(user, incident_type: str, description: str):
        """Güvenlik olayı bildirimi"""
        title = "🔒 Güvenlik Olayı"
        message = f"Güvenlik olayı tespit edildi: {incident_type}\n\n"
        message += f"Açıklama: {description}\n\n"
        message += "Lütfen hesap güvenliğinizi kontrol edin."
        
        action_url = "/accounts/settings/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="error",
            priority="urgent",
            action_url=action_url,
            category="security",
            module="security",
            send_email=True,
        )
    
    @staticmethod
    def notify_api_limit_warning(user, usage_percent: int):
        """API kullanım limiti uyarısı"""
        title = f"⚠️ API Kullanım Limitiniz %{usage_percent}"
        message = f"API kullanım limitinizin %{usage_percent}'ine ulaştınız.\n\n"
        message += "Limit aşılmadan önce planınızı yükseltmeyi düşünün."
        
        action_url = "/billing/plans/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="normal",
            action_url=action_url,
            category="api",
            module="developer_portal",
            send_email=False,
        )
    
    @staticmethod
    def notify_storage_limit_warning(user, usage_percent: int):
        """Depolama limiti uyarısı"""
        title = f"💾 Depolama Limitiniz %{usage_percent}"
        message = f"Depolama kullanımınızın %{usage_percent}'ine ulaştınız.\n\n"
        message += "Limit aşılmadan önce planınızı yükseltmeyi veya eski dosyaları temizlemeyi düşünün."
        
        action_url = "/accounts/settings/"
        
        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type="warning",
            priority="normal",
            action_url=action_url,
            category="storage",
            module="common",
            send_email=False,
        )

