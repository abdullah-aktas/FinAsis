# -*- coding: utf-8 -*-
"""
Mali Müşavirlik Modülü Signal Handlers
Otomatik işlemler için signal'ler
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models_marketplace import (
    ConsultantProfile,
    ConsultationBooking,
    ConsultationPayment,
    ConsultantPayout,
    ConsultantReview,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ConsultantProfile)
def consultant_profile_post_save(sender, instance, created, **kwargs):
    """
    ConsultantProfile kaydedildiğinde:
    - Onaylandığında blockchain anlaşması oluştur
    """
    if not created:
        # Güncelleme durumunda
        if (
            instance.approval_status == "approved"
            and not instance.blockchain_contract_address
        ):
            # Onaylandı ama blockchain anlaşması yok
            try:
                from .services.blockchain_service import create_agreement_on_approval

                # Admin kullanıcısını bul (veya sistem kullanıcısı)
                from django.contrib.auth import get_user_model

                User = get_user_model()
                admin_user = User.objects.filter(is_superuser=True).first()

                if admin_user and instance.can_be_approved():
                    result = create_agreement_on_approval(instance, admin_user)
                    logger.info(
                        f"Blockchain anlaşması oluşturuldu: {instance.display_name} - {result.get('contract_address', 'N/A')}"
                    )
            except Exception as e:
                logger.error(f"Blockchain anlaşması oluşturulamadı: {str(e)}")


@receiver(post_save, sender=ConsultationBooking)
def consultation_booking_post_save(sender, instance, created, **kwargs):
    """
    ConsultationBooking kaydedildiğinde:
    - Onaylandığında otomatik toplantı oluştur
    - Tamamlandığında istatistikleri güncelle
    """
    if not created:
        # Güncelleme durumunda
        if instance.status == "confirmed" and not instance.meeting_url:
            # Onaylandı ama toplantı oluşturulmamış
            try:
                instance.ensure_online_meeting()
                logger.info(f"Toplantı oluşturuldu: {instance.booking_number}")
            except Exception as e:
                logger.error(f"Toplantı oluşturulamadı: {str(e)}")

        elif instance.status == "completed":
            # Tamamlandı - istatistikleri güncelle
            try:
                # ConsultantProfile istatistikleri zaten model'de güncelleniyor
                # Burada ek işlemler yapılabilir
                if not instance.actual_end_time:
                    instance.actual_end_time = timezone.now()
                    instance.save(update_fields=["actual_end_time"])
            except Exception as e:
                logger.error(f"İstatistik güncelleme hatası: {str(e)}")


@receiver(post_save, sender=ConsultationPayment)
def consultation_payment_post_save(sender, instance, created, **kwargs):
    """
    ConsultationPayment kaydedildiğinde:
    - Ödeme tamamlandığında payout oluştur
    """
    if not created:
        # Güncelleme durumunda
        if instance.status == "completed" and not instance.payout_to_consultant_at:
            # Ödeme tamamlandı ama payout oluşturulmamış
            try:
                # Aylık payout oluştur (veya mevcut payout'a ekle)
                from datetime import timedelta

                now = timezone.now()
                period_start = now.replace(day=1).date()  # Ayın ilk günü
                period_end = (now.replace(day=28) + timedelta(days=4)).replace(
                    day=1
                ) - timedelta(
                    days=1
                )  # Ayın son günü

                # Mevcut payout var mı kontrol et
                payout, created = ConsultantPayout.objects.get_or_create(
                    consultant=instance.consultant,
                    period_start=period_start,
                    period_end=period_end,
                    status="pending",
                    defaults={
                        "amount": instance.consultant_amount,
                        "currency": instance.currency,
                        "bank_name": "",  # Mali müşavirden alınacak
                        "account_holder": "",
                        "iban": "",
                        "included_payments": [instance.id],
                    },
                )

                if not created:
                    # Mevcut payout'a ekle
                    payout.amount += instance.consultant_amount
                    if instance.id not in payout.included_payments:
                        payout.included_payments.append(instance.id)
                    payout.save()

                # Payout tarihini güncelle
                instance.payout_to_consultant_at = now
                instance.save(update_fields=["payout_to_consultant_at"])

                logger.info(
                    f"Payout oluşturuldu/güncellendi: {payout.id} - {instance.consultant.display_name}"
                )
            except Exception as e:
                logger.error(f"Payout oluşturulamadı: {str(e)}")


@receiver(pre_save, sender=ConsultationBooking)
def consultation_booking_pre_save(sender, instance, **kwargs):
    """
    ConsultationBooking kaydedilmeden önce:
    - Komisyon ve kazanç hesapla
    """
    if instance.final_price or instance.quoted_price:
        # Fiyat varsa komisyon hesapla
        try:
            instance.calculate_commission()
        except Exception as e:
            logger.error(f"Komisyon hesaplanamadı: {str(e)}")


@receiver(post_save, sender=ConsultantReview)
def consultant_review_post_save(sender, instance, created, **kwargs):
    """
    ConsultantReview kaydedildiğinde:
    - ConsultantProfile rating'ini güncelle
    """
    try:
        instance.consultant.update_rating()
        logger.info(
            f"Rating güncellendi: {instance.consultant.display_name} - {instance.consultant.average_rating}"
        )
    except Exception as e:
        logger.error(f"Rating güncelleme hatası: {str(e)}")
