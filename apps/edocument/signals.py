from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    EDocument, EDocumentLog, EDocumentItem,
    EDespatchAdvice, EDespatchAdviceLog, EDespatchAdviceItem,
    Document, DocumentLog, DocumentVersion
)

@receiver(pre_save, sender=EDocument)
def document_pre_save(sender, instance, **kwargs):
    """E-Fatura kaydetme öncesi işlemler"""
    if not instance.pk:  # Yeni kayıt
        instance.status = 'DRAFT'
    else:  # Güncelleme
        old_instance = EDocument.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            # Durum değişikliği logla
            EDocumentLog.objects.create(
                document=instance,
                action='STATUS_CHANGE',
                status=instance.status,
                message=f'Durum {old_instance.status} -> {instance.status} olarak değiştirildi'
            )

@receiver(post_save, sender=EDocument)
def document_post_save(sender, instance, created, **kwargs):
    """E-Fatura kaydetme sonrası işlemler"""
    if created:
        # Yeni kayıt logla
        EDocumentLog.objects.create(
            document=instance,
            action='CREATE',
            status=instance.status,
            message='Yeni fatura oluşturuldu'
        )

@receiver(pre_delete, sender=EDocument)
def document_pre_delete(sender, instance, **kwargs):
    """E-Fatura silme öncesi işlemler"""
    if instance.status != 'DRAFT':
        raise Exception('Sadece taslak durumundaki belgeler silinebilir')
    
    # Silme işlemi logla
    EDocumentLog.objects.create(
        document=instance,
        action='DELETE',
        status=instance.status,
        message='Fatura silindi'
    )

@receiver(pre_save, sender=EDespatchAdvice)
def despatch_pre_save(sender, instance, **kwargs):
    """E-İrsaliye kaydetme öncesi işlemler"""
    if not instance.pk:  # Yeni kayıt
        instance.status = 'DRAFT'
    else:  # Güncelleme
        old_instance = EDespatchAdvice.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            # Durum değişikliği logla
            EDespatchAdviceLog.objects.create(
                despatch=instance,
                action='STATUS_CHANGE',
                status=instance.status,
                message=f'Durum {old_instance.status} -> {instance.status} olarak değiştirildi'
            )

@receiver(post_save, sender=EDespatchAdvice)
def despatch_post_save(sender, instance, created, **kwargs):
    """E-İrsaliye kaydetme sonrası işlemler"""
    if created:
        # Yeni kayıt logla
        EDespatchAdviceLog.objects.create(
            despatch=instance,
            action='CREATE',
            status=instance.status,
            message='Yeni irsaliye oluşturuldu'
        )

@receiver(pre_delete, sender=EDespatchAdvice)
def despatch_pre_delete(sender, instance, **kwargs):
    """E-İrsaliye silme öncesi işlemler"""
    if instance.status != 'DRAFT':
        raise Exception('Sadece taslak durumundaki belgeler silinebilir')
    
    # Silme işlemi logla
    EDespatchAdviceLog.objects.create(
        despatch=instance,
        action='DELETE',
        status=instance.status,
        message='İrsaliye silindi'
    )

@receiver(pre_save, sender=EDocumentItem)
def document_item_pre_save(sender, instance, **kwargs):
    """E-Fatura kalemi kaydetme öncesi işlemler"""
    if not instance.pk:  # Yeni kayıt
        # Sıra numarası ata
        last_item = EDocumentItem.objects.filter(document=instance.document).order_by('-line_number').first()
        instance.line_number = (last_item.line_number + 1) if last_item else 1

@receiver(pre_save, sender=EDespatchAdviceItem)
def despatch_item_pre_save(sender, instance, **kwargs):
    """E-İrsaliye kalemi kaydetme öncesi işlemler"""
    if not instance.pk:  # Yeni kayıt
        # Sıra numarası ata
        last_item = EDespatchAdviceItem.objects.filter(despatch=instance.despatch).order_by('-line_number').first()
        instance.line_number = (last_item.line_number + 1) if last_item else 1

@receiver(post_save, sender=Document)
def create_document_log(sender, instance, created, **kwargs):
    """Doküman oluşturulduğunda veya güncellendiğinde log kaydı oluştur"""
    action = 'created' if created else 'updated'
    DocumentLog.objects.create(
        document=instance,
        action=action,
        user=instance.user,
        details=f'Document {action}'
    )

@receiver(pre_save, sender=Document)
def update_document_version(sender, instance, **kwargs):
    """Doküman güncellendiğinde versiyon numarasını artır"""
    if instance.pk:  # Yeni oluşturulmuyorsa
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            if old_instance.file != instance.file:
                # Dosya değiştiyse yeni versiyon oluştur
                from .models import DocumentVersion
                DocumentVersion.objects.create(
                    document=instance,
                    file=instance.file,
                    version_number=old_instance.versions.count() + 1,
                    created_by=instance.user
                )
        except Document.DoesNotExist:
            pass 