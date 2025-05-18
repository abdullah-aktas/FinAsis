# -*- coding: utf-8 -*-
from django.db.models.signals import (
    pre_save, post_save, pre_delete,
    post_delete, m2m_changed
)
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from .models import (
    Customer, Contact, Opportunity, Activity,
    Document, Communication, Note,
    LoyaltyProgram, LoyaltyLevel, CustomerLoyalty,
    SeasonalCampaign, PartnershipProgram, Partner,
    InteractionLog
)
import logging

logger = logging.getLogger(__name__)

# Müşteri sinyalleri
@receiver(pre_save, sender=Customer)
def customer_pre_save(sender, instance, **kwargs):
    """Müşteri kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:  # Yeni kayıt
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()
    
    # Kredi skoru kontrolü
    if instance.credit_score < 0:
        instance.credit_score = 0
    elif instance.credit_score > 1000:
        instance.credit_score = 1000

@receiver(post_save, sender=Customer)
def customer_post_save(sender, instance, created, **kwargs):
    """Müşteri kaydedildikten sonra yapılacak işlemler"""
    if created:
        # Yeni müşteri için varsayılan sadakat programı oluştur
        default_program = LoyaltyProgram.objects.filter(is_default=True).first()
        if default_program:
            CustomerLoyalty.objects.create(
                customer=instance,
                program=default_program,
                current_level=default_program.levels.first()
            )
        logger.info(f"Yeni müşteri oluşturuldu: {instance.company_name}")

# İletişim kişisi sinyalleri
@receiver(pre_save, sender=Contact)
def contact_pre_save(sender, instance, **kwargs):
    """İletişim kişisi kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()
    
    # Birincil iletişim kişisi kontrolü
    if instance.is_primary:
        Contact.objects.filter(
            customer=instance.customer,
            is_primary=True
        ).exclude(pk=instance.pk).update(is_primary=False)

@receiver(post_save, sender=Contact)
def contact_post_save(sender, instance, created, **kwargs):
    """İletişim kişisi kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni iletişim kişisi oluşturuldu: {instance.first_name} {instance.last_name}")

# Fırsat sinyalleri
@receiver(pre_save, sender=Opportunity)
def opportunity_pre_save(sender, instance, **kwargs):
    """Fırsat kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()
    
    # Olasılık kontrolü
    if instance.probability < 0:
        instance.probability = 0
    elif instance.probability > 100:
        instance.probability = 100

@receiver(post_save, sender=Opportunity)
def opportunity_post_save(sender, instance, created, **kwargs):
    """Fırsat kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni fırsat oluşturuldu: {instance.title}")
    elif instance.status == 'won':
        # Kazanılan fırsat için sadakat puanı ekle
        try:
            customer_loyalty = CustomerLoyalty.objects.get(customer=instance.customer)
            points = int(instance.amount * 0.01)  # Tutarın %1'i kadar puan
            customer_loyalty.total_points += points
            customer_loyalty.save()
            logger.info(f"Fırsat kazanıldı: {instance.title}, {points} puan eklendi")
        except CustomerLoyalty.DoesNotExist:
            logger.warning(f"Sadakat programı bulunamadı: {instance.customer.company_name}")

# Aktivite sinyalleri
@receiver(pre_save, sender=Activity)
def activity_pre_save(sender, instance, **kwargs):
    """Aktivite kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()
    
    # Tamamlanma kontrolü
    if instance.completed and not instance.completed_at:
        instance.completed_at = timezone.now()

@receiver(post_save, sender=Activity)
def activity_post_save(sender, instance, created, **kwargs):
    """Aktivite kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni aktivite oluşturuldu: {instance.subject}")

# Doküman sinyalleri
@receiver(pre_save, sender=Document)
def document_pre_save(sender, instance, **kwargs):
    """Doküman kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    """Doküman kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni doküman yüklendi: {instance.title}")

# İletişim sinyalleri
@receiver(pre_save, sender=Communication)
def communication_pre_save(sender, instance, **kwargs):
    """İletişim kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=Communication)
def communication_post_save(sender, instance, created, **kwargs):
    """İletişim kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni iletişim kaydı oluşturuldu: {instance.subject}")

# Not sinyalleri
@receiver(pre_save, sender=Note)
def note_pre_save(sender, instance, **kwargs):
    """Not kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=Note)
def note_post_save(sender, instance, created, **kwargs):
    """Not kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni not oluşturuldu: {instance.title}")

# Sadakat programı sinyalleri
@receiver(pre_save, sender=LoyaltyProgram)
def loyalty_program_pre_save(sender, instance, **kwargs):
    """Sadakat programı kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=LoyaltyProgram)
def loyalty_program_post_save(sender, instance, created, **kwargs):
    """Sadakat programı kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni sadakat programı oluşturuldu: {instance.name}")

# Sadakat seviyesi sinyalleri
@receiver(pre_save, sender=LoyaltyLevel)
def loyalty_level_pre_save(sender, instance, **kwargs):
    """Sadakat seviyesi kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=LoyaltyLevel)
def loyalty_level_post_save(sender, instance, created, **kwargs):
    """Sadakat seviyesi kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni sadakat seviyesi oluşturuldu: {instance.name}")

# Müşteri sadakati sinyalleri
@receiver(pre_save, sender=CustomerLoyalty)
def customer_loyalty_pre_save(sender, instance, **kwargs):
    """Müşteri sadakati kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()
    
    # Sadakat seviyesi güncelleme
    if instance.total_points >= instance.current_level.max_points:
        next_level = instance.program.levels.filter(
            min_points__gt=instance.current_level.min_points
        ).order_by('min_points').first()
        if next_level:
            instance.current_level = next_level

@receiver(post_save, sender=CustomerLoyalty)
def customer_loyalty_post_save(sender, instance, created, **kwargs):
    """Müşteri sadakati kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni müşteri sadakati oluşturuldu: {instance.customer.company_name}")

# Sezonluk kampanya sinyalleri
@receiver(pre_save, sender=SeasonalCampaign)
def seasonal_campaign_pre_save(sender, instance, **kwargs):
    """Sezonluk kampanya kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=SeasonalCampaign)
def seasonal_campaign_post_save(sender, instance, created, **kwargs):
    """Sezonluk kampanya kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni sezonluk kampanya oluşturuldu: {instance.name}")

# Ortaklık programı sinyalleri
@receiver(pre_save, sender=PartnershipProgram)
def partnership_program_pre_save(sender, instance, **kwargs):
    """Ortaklık programı kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=PartnershipProgram)
def partnership_program_post_save(sender, instance, created, **kwargs):
    """Ortaklık programı kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni ortaklık programı oluşturuldu: {instance.name}")

# Ortak sinyalleri
@receiver(pre_save, sender=Partner)
def partner_pre_save(sender, instance, **kwargs):
    """Ortak kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=Partner)
def partner_post_save(sender, instance, created, **kwargs):
    """Ortak kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni ortak oluşturuldu: {instance.name}")

# Etkileşim log sinyalleri
@receiver(pre_save, sender=InteractionLog)
def interaction_log_pre_save(sender, instance, **kwargs):
    """Etkileşim log kaydedilmeden önce yapılacak işlemler"""
    if not instance.pk:
        instance.created_at = timezone.now()
    instance.updated_at = timezone.now()

@receiver(post_save, sender=InteractionLog)
def interaction_log_post_save(sender, instance, created, **kwargs):
    """Etkileşim log kaydedildikten sonra yapılacak işlemler"""
    if created:
        logger.info(f"Yeni etkileşim log oluşturuldu: {instance.type}")

# Silme işlemleri için sinyaller
@receiver(pre_delete, sender=Customer)
def customer_pre_delete(sender, instance, **kwargs):
    """Müşteri silinmeden önce yapılacak işlemler"""
    logger.warning(f"Müşteri siliniyor: {instance.company_name}")

@receiver(pre_delete, sender=Contact)
def contact_pre_delete(sender, instance, **kwargs):
    """İletişim kişisi silinmeden önce yapılacak işlemler"""
    logger.warning(f"İletişim kişisi siliniyor: {instance.first_name} {instance.last_name}")

@receiver(pre_delete, sender=Opportunity)
def opportunity_pre_delete(sender, instance, **kwargs):
    """Fırsat silinmeden önce yapılacak işlemler"""
    logger.warning(f"Fırsat siliniyor: {instance.title}")

@receiver(pre_delete, sender=Activity)
def activity_pre_delete(sender, instance, **kwargs):
    """Aktivite silinmeden önce yapılacak işlemler"""
    logger.warning(f"Aktivite siliniyor: {instance.subject}")

@receiver(pre_delete, sender=Document)
def document_pre_delete(sender, instance, **kwargs):
    """Doküman silinmeden önce yapılacak işlemler"""
    logger.warning(f"Doküman siliniyor: {instance.title}")

@receiver(pre_delete, sender=Communication)
def communication_pre_delete(sender, instance, **kwargs):
    """İletişim silinmeden önce yapılacak işlemler"""
    logger.warning(f"İletişim siliniyor: {instance.subject}")

@receiver(pre_delete, sender=Note)
def note_pre_delete(sender, instance, **kwargs):
    """Not silinmeden önce yapılacak işlemler"""
    logger.warning(f"Not siliniyor: {instance.title}") 