from django.db import models
from django.conf import settings


class Declaration(models.Model):
    code = models.CharField(max_length=50)  # e.g., KDV1, BA-BS, Muhtasar
    period = models.CharField(max_length=20)  # e.g., 2025-01
    taxpayer_vkn_tckn = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)  # normalized data to render XML/JSON for GIB
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['code', 'period', 'taxpayer_vkn_tckn'])
        ]


class Submission(models.Model):
    TARGETS = (
        ('gib', 'GIB'),
    )
    declaration = models.ForeignKey(Declaration, on_delete=models.CASCADE, related_name='submissions')
    target = models.CharField(max_length=10, choices=TARGETS, default='gib')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    advisor_required = models.BooleanField(default=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='draft')  # draft|queued|sent|accepted|rejected
    external_id = models.CharField(max_length=100, blank=True)  # integrator tracking id


class SubmissionLog(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=10, default='info')
    message = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# ============================================================================
# GENİŞLETİLMİŞ BEYAN/GÖNDERİM SİSTEMİ
# ============================================================================

class SubmissionTemplate(models.Model):
    """Beyan şablonları - tekrar kullanılabilir şablonlar"""
    
    name = models.CharField(max_length=200, verbose_name='Şablon Adı')
    code = models.CharField(max_length=50, verbose_name='Beyan Kodu', help_text='KDV1, BA-BS, Muhtasar, vs.')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    
    # Şablon yapısı
    template_structure = models.JSONField(default=dict, verbose_name='Şablon Yapısı')
    default_values = models.JSONField(default=dict, blank=True, verbose_name='Varsayılan Değerler')
    validation_rules = models.JSONField(default=dict, blank=True, verbose_name='Doğrulama Kuralları')
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    version = models.CharField(max_length=20, default='1.0', verbose_name='Versiyon')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Beyan Şablonu'
        verbose_name_plural = 'Beyan Şablonları'
        ordering = ['code', 'name']
        unique_together = ['code', 'version']
    
    def __str__(self):
        return f"{self.code} - {self.name} (v{self.version})"


class SubmissionAttachment(models.Model):
    """Beyan ekleri - belgeler"""
    
    ATTACHMENT_TYPES = [
        ('PDF', 'PDF Belgesi'),
        ('XML', 'XML Dosyası'),
        ('EXCEL', 'Excel Dosyası'),
        ('IMAGE', 'Görsel'),
        ('OTHER', 'Diğer'),
    ]
    
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='attachments', verbose_name='Beyan')
    
    file = models.FileField(upload_to='submissions/attachments/', verbose_name='Dosya')
    file_name = models.CharField(max_length=255, verbose_name='Dosya Adı')
    file_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, verbose_name='Dosya Tipi')
    file_size = models.BigIntegerField(verbose_name='Dosya Boyutu (bytes)')
    
    description = models.TextField(blank=True, verbose_name='Açıklama')
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Yükleyen')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Beyan Eki'
        verbose_name_plural = 'Beyan Ekleri'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.submission.id} - {self.file_name}"


class SubmissionApproval(models.Model):
    """Beyan onay süreci"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Beklemede'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
        ('REVISION_REQUESTED', 'Revizyon İstendi'),
    ]
    
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='approvals', verbose_name='Beyan')
    
    # Onay bilgisi
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submission_approvals', verbose_name='Onaylayan')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING', verbose_name='Durum')
    
    # Yorum
    comments = models.TextField(blank=True, verbose_name='Yorumlar')
    revision_notes = models.TextField(blank=True, verbose_name='Revizyon Notları')
    
    # Tarihler
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='İstek Tarihi')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Yanıt Tarihi')
    
    class Meta:
        verbose_name = 'Beyan Onayı'
        verbose_name_plural = 'Beyan Onayları'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.submission.id} - {self.approver.username} ({self.status})"