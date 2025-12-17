# -*- coding: utf-8 -*-
"""
Billing Notification Service
Ödeme onaylandığında otomatik bildirim ve mail gönderimi
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from accounts.models import UserNotification

logger = logging.getLogger(__name__)


class BillingNotificationService:
    """Faturalandırma bildirim servisi"""
    
    @staticmethod
    def send_payment_confirmation(subscription_profile, transaction, invoice=None):
        """Ödeme onayı bildirimi ve mail gönder"""
        user = subscription_profile.user
        
        try:
            # 1. Bildirim oluştur
            notification = UserNotification.objects.create(
                user=user,
                title="Ödeme Onaylandı",
                message=(
                    f"{subscription_profile.plan.name if subscription_profile.plan else 'Abonelik'} "
                    f"için ödemeniz onaylandı. Fatura ve sözleşme bilgileri e-posta adresinize gönderildi."
                ),
                notification_type="payment_confirmed",
                is_read=False,
                metadata={
                    "subscription_id": str(subscription_profile.id),
                    "transaction_id": str(transaction.id),
                    "invoice_id": str(invoice.id) if invoice else None,
                    "amount": str(transaction.amount),
                }
            )
            
            # 2. E-posta gönder
            BillingNotificationService._send_payment_email(
                user,
                subscription_profile,
                transaction,
                invoice
            )
            
            logger.info(
                f"Ödeme onayı bildirimi gönderildi: User {user.username}, "
                f"Transaction {transaction.id}"
            )
            
            return notification
            
        except Exception as e:
            logger.error(
                f"Ödeme onayı bildirimi hatası: {e}",
                exc_info=True
            )
            return None
    
    @staticmethod
    def _send_payment_email(user, subscription_profile, transaction, invoice=None):
        """Ödeme onayı e-postası gönder"""
        try:
            plan = subscription_profile.plan
            
            # Blockchain sözleşme bilgisi
            from billing.services.blockchain_contract import SubscriptionBlockchainService
            contracts = SubscriptionBlockchainService.get_user_contracts(user)
            contract = contracts.first() if contracts.exists() else None
            
            context = {
                "user": user,
                "subscription": subscription_profile,
                "plan": plan,
                "transaction": transaction,
                "invoice": invoice,
                "contract": contract,
                "site_url": getattr(settings, "SITE_URL", "https://finasis.com.tr"),
                "support_email": getattr(settings, "SUPPORT_EMAIL", "destek@finasis.com.tr"),
            }
            
            # HTML e-posta içeriği
            html_content = render_to_string(
                "billing/emails/payment_confirmation.html",
                context
            )
            
            # Plain text versiyonu
            text_content = strip_tags(html_content)
            
            # E-posta gönder
            subject = f"Ödeme Onaylandı - {plan.name if plan else 'Abonelik'}"
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@finasis.com.tr"),
                to=[user.email],
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Fatura PDF ekle (varsa)
            if invoice:
                # Fatura PDF oluştur ve ekle
                # TODO: PDF oluşturma servisi entegre et
                pass
            
            email.send()
            
            logger.info(f"Ödeme onayı e-postası gönderildi: {user.email}")
            
        except Exception as e:
            logger.error(
                f"Ödeme onayı e-postası gönderme hatası: {e}",
                exc_info=True
            )
    
    @staticmethod
    def send_contract_notification(user, contract):
        """Blockchain sözleşme bildirimi gönder"""
        try:
            # Bildirim oluştur
            notification = UserNotification.objects.create(
                user=user,
                title="Blockchain Sözleşme Oluşturuldu",
                message=(
                    f"Aboneliğiniz için blockchain sözleşmesi oluşturuldu. "
                    f"Sözleşme adresi: {contract.contract_address[:16]}..."
                ),
                notification_type="blockchain_contract",
                is_read=False,
                metadata={
                    "contract_address": contract.contract_address,
                    "contract_type": contract.contract_type,
                }
            )
            
            # E-posta gönder
            context = {
                "user": user,
                "contract": contract,
                "site_url": getattr(settings, "SITE_URL", "https://finasis.com.tr"),
                "contract_url": f"{getattr(settings, 'SITE_URL', 'https://finasis.com.tr')}/blockchain/contracts/{contract.contract_address}/",
            }
            
            html_content = render_to_string(
                "billing/emails/contract_created.html",
                context
            )
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject="Blockchain Sözleşme Oluşturuldu - FinAsis",
                body=text_content,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@finasis.com.tr"),
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(
                f"Blockchain sözleşme bildirimi gönderildi: User {user.username}, "
                f"Contract {contract.contract_address}"
            )
            
            return notification
            
        except Exception as e:
            logger.error(
                f"Blockchain sözleşme bildirimi hatası: {e}",
                exc_info=True
            )
            return None
    
    @staticmethod
    def send_invoice_email(user, invoice):
        """Fatura e-postası gönder"""
        try:
            context = {
                "user": user,
                "invoice": invoice,
                "subscription": invoice.subscription,
                "plan": invoice.subscription.plan if invoice.subscription.plan else None,
                "site_url": getattr(settings, "SITE_URL", "https://finasis.com.tr"),
            }
            
            html_content = render_to_string(
                "billing/emails/invoice.html",
                context
            )
            text_content = strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject=f"Fatura - {invoice.invoice_number}",
                body=text_content,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@finasis.com.tr"),
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            
            # Fatura PDF ekle
            # TODO: PDF oluşturma servisi entegre et
            
            email.send()
            
            logger.info(f"Fatura e-postası gönderildi: {user.email}, Invoice {invoice.invoice_number}")
            
        except Exception as e:
            logger.error(
                f"Fatura e-postası gönderme hatası: {e}",
                exc_info=True
            )

