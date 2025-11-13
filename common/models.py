from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# Import ErrorLog from error_tracking module
from .error_tracking import ErrorLog  # noqa: F401

class AuditLog(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    content_object = GenericForeignKey('content_type', 'object_id')
    action = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['content_type','object_id','created_at']),
            models.Index(fields=['action','created_at']),
        ]
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    def __str__(self):
        return f"{self.action} @ {self.created_at}"
    @classmethod
    def log_action(cls, obj, action, user=None, ip=None, payload=None):
        return cls.objects.create(
            content_type=ContentType.objects.get_for_model(obj.__class__),
            object_id=str(getattr(obj, 'pk', getattr(obj, 'id', ''))),
            action=action, user=user, ip_address=ip, payload=payload or {},
        )

class ApprovalRequest(models.Model):
    STATUS = (('PENDING','Beklemede'),('APPROVED','Onaylandı'),('REJECTED','Reddedildi'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='common_approval_requests')
    object_id = models.CharField(max_length=64)
    content_object = GenericForeignKey('content_type', 'object_id')
    status = models.CharField(max_length=16, choices=STATUS, default='PENDING')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='approvals_requested', on_delete=models.CASCADE)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='approvals_decided', on_delete=models.SET_NULL)
    decided_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['content_type','object_id','status']),
            models.Index(fields=['created_at'])
        ]
        ordering = ['-created_at']
    def approve(self, user, comment=''):
        self.status='APPROVED'; self.decided_by=user; self.decided_at=timezone.now(); self.comment = comment or self.comment
        self.save(update_fields=['status','decided_by','decided_at','comment'])
    def reject(self, user, comment=''):
        self.status='REJECTED'; self.decided_by=user; self.decided_at=timezone.now(); self.comment = comment or self.comment
        self.save(update_fields=['status','decided_by','decided_at','comment'])


# ============================================================================
# GENİŞLETİLMİŞ ORTAK SERVİSLER
# ============================================================================

class SystemSetting(models.Model):
    """Sistem ayarları - key-value store"""
    SETTING_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('text', 'Text'),
    ]
    
    key = models.CharField(max_length=100, unique=True, verbose_name="Anahtar")
    value = models.TextField(verbose_name="Değer")
    value_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string', verbose_name="Tip")
    
    description = models.TextField(blank=True, verbose_name="Açıklama")
    category = models.CharField(max_length=50, blank=True, verbose_name="Kategori")
    
    is_public = models.BooleanField(default=False, verbose_name="Herkese Açık")
    is_editable = models.BooleanField(default=True, verbose_name="Düzenlenebilir")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Güncelleyen")
    
    class Meta:
        verbose_name = "Sistem Ayarı"
        verbose_name_plural = "Sistem Ayarları"
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key} = {self.value}"
    
    def get_value(self):
        """Tipine göre değeri döndür"""
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class FileUpload(models.Model):
    """Dosya yükleme yönetimi"""
    FILE_CATEGORIES = [
        ('document', 'Doküman'),
        ('image', 'Görsel'),
        ('video', 'Video'),
        ('audio', 'Ses'),
        ('spreadsheet', 'Tablo'),
        ('archive', 'Arşiv'),
        ('other', 'Diğer'),
    ]
    
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name="Dosya")
    original_filename = models.CharField(max_length=255, verbose_name="Orijinal Dosya Adı")
    file_size = models.BigIntegerField(verbose_name="Dosya Boyutu (bytes)")
    file_type = models.CharField(max_length=100, verbose_name="Dosya Tipi (MIME)")
    category = models.CharField(max_length=20, choices=FILE_CATEGORIES, default='other', verbose_name="Kategori")
    
    # İlişki
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files', verbose_name="Yükleyen")
    
    # Generic relation
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadata
    description = models.TextField(blank=True, verbose_name="Açıklama")
    tags = models.JSONField(default=list, blank=True, verbose_name="Etiketler")
    
    # Güvenlik
    is_public = models.BooleanField(default=False, verbose_name="Herkese Açık")
    access_count = models.IntegerField(default=0, verbose_name="Erişim Sayısı")
    
    # Virus scan
    is_scanned = models.BooleanField(default=False, verbose_name="Tarandı")
    is_safe = models.BooleanField(default=True, verbose_name="Güvenli")
    scan_result = models.TextField(blank=True, verbose_name="Tarama Sonucu")
    
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Yüklenme Tarihi")
    
    class Meta:
        verbose_name = "Dosya Yükleme"
        verbose_name_plural = "Dosya Yüklemeleri"
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['uploaded_by', '-uploaded_at']),
            models.Index(fields=['category', '-uploaded_at']),
        ]
    
    def __str__(self):
        return self.original_filename


class EmailTemplate(models.Model):
    """E-posta şablonları"""
    code = models.CharField(max_length=50, unique=True, verbose_name="Kod")
    name = models.CharField(max_length=200, verbose_name="Şablon Adı")
    subject = models.CharField(max_length=200, verbose_name="Konu")
    body_html = models.TextField(verbose_name="HTML İçerik")
    body_text = models.TextField(blank=True, verbose_name="Düz Metin İçerik")
    
    # Değişkenler
    variables = models.JSONField(default=list, blank=True, verbose_name="Değişkenler", help_text="Kullanılabilir değişkenler: {{user}}, {{company}}, vs.")
    
    # Kategori
    category = models.CharField(max_length=50, blank=True, verbose_name="Kategori")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Oluşturan")
    
    class Meta:
        verbose_name = "E-posta Şablonu"
        verbose_name_plural = "E-posta Şablonları"
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class EmailLog(models.Model):
    """E-posta gönderim logları"""
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('sent', 'Gönderildi'),
        ('failed', 'Başarısız'),
        ('bounced', 'Geri Döndü'),
    ]
    
    template = models.ForeignKey(EmailTemplate, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Şablon")
    
    to_email = models.EmailField(verbose_name="Alıcı")
    cc_emails = models.TextField(blank=True, verbose_name="CC")
    bcc_emails = models.TextField(blank=True, verbose_name="BCC")
    
    subject = models.CharField(max_length=200, verbose_name="Konu")
    body = models.TextField(verbose_name="İçerik")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")
    
    # İstatistikler
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Gönderim Zamanı")
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name="Açılma Zamanı")
    clicked_at = models.DateTimeField(null=True, blank=True, verbose_name="Tıklama Zamanı")
    
    # İlişki
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Kullanıcı")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "E-posta Logu"
        verbose_name_plural = "E-posta Logları"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['to_email', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.to_email} - {self.subject} ({self.status})"


class APIKey(models.Model):
    """API anahtarları"""
    name = models.CharField(max_length=200, verbose_name="Anahtar Adı")
    key = models.CharField(max_length=100, unique=True, verbose_name="API Key")
    secret = models.CharField(max_length=100, blank=True, verbose_name="Secret Key")
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='api_keys', verbose_name="Kullanıcı")
    
    # İzinler
    permissions = models.JSONField(default=list, blank=True, verbose_name="İzinler")
    allowed_ips = models.TextField(blank=True, verbose_name="İzin Verilen IP'ler", help_text="Her satırda bir IP")
    
    # Rate limiting
    rate_limit = models.IntegerField(default=1000, verbose_name="Rate Limit (saat başı)")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # İstatistikler
    total_requests = models.IntegerField(default=0, verbose_name="Toplam İstek")
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="Son Kullanım")
    
    # Geçerlilik
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Geçerlilik Süresi")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "API Anahtarı"
        verbose_name_plural = "API Anahtarları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def is_valid(self):
        """Anahtarın geçerli olup olmadığını kontrol et"""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class Webhook(models.Model):
    """Webhook yönetimi"""
    EVENT_TYPES = [
        ('user.created', 'Kullanıcı Oluşturuldu'),
        ('user.updated', 'Kullanıcı Güncellendi'),
        ('invoice.created', 'Fatura Oluşturuldu'),
        ('invoice.paid', 'Fatura Ödendi'),
        ('payment.completed', 'Ödeme Tamamlandı'),
        ('subscription.renewed', 'Abonelik Yenilendi'),
        ('custom', 'Özel'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Webhook Adı")
    url = models.URLField(verbose_name="Webhook URL")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Event Tipi")
    
    # Güvenlik
    secret_key = models.CharField(max_length=100, blank=True, verbose_name="Secret Key")
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # İstatistikler
    total_calls = models.IntegerField(default=0, verbose_name="Toplam Çağrı")
    success_count = models.IntegerField(default=0, verbose_name="Başarılı")
    failure_count = models.IntegerField(default=0, verbose_name="Başarısız")
    last_called_at = models.DateTimeField(null=True, blank=True, verbose_name="Son Çağrı")
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='webhooks', verbose_name="Kullanıcı")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.event_type}"


class WebhookLog(models.Model):
    """Webhook çağrı logları"""
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='logs', verbose_name="Webhook")
    
    # Request
    request_payload = models.JSONField(default=dict, verbose_name="İstek")
    request_headers = models.JSONField(default=dict, verbose_name="İstek Headers")
    
    # Response
    response_status = models.IntegerField(null=True, blank=True, verbose_name="Durum Kodu")
    response_body = models.TextField(blank=True, verbose_name="Yanıt")
    response_time_ms = models.IntegerField(null=True, blank=True, verbose_name="Yanıt Süresi (ms)")
    
    # Durum
    is_success = models.BooleanField(default=False, verbose_name="Başarılı")
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")
    
    # Retry
    retry_count = models.IntegerField(default=0, verbose_name="Yeniden Deneme Sayısı")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Webhook Logu"
        verbose_name_plural = "Webhook Logları"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', '-created_at']),
            models.Index(fields=['is_success', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.webhook.name} - {self.created_at}"


class ScheduledTask(models.Model):
    """Zamanlanmış görevler"""
    TASK_TYPES = [
        ('email', 'E-posta Gönder'),
        ('report', 'Rapor Oluştur'),
        ('backup', 'Yedekleme'),
        ('cleanup', 'Temizlik'),
        ('reminder', 'Hatırlatıcı'),
        ('custom', 'Özel'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('running', 'Çalışıyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Görev Adı")
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, verbose_name="Görev Tipi")
    
    # Zamanlama
    scheduled_at = models.DateTimeField(verbose_name="Çalışma Zamanı")
    is_recurring = models.BooleanField(default=False, verbose_name="Tekrarlayan")
    recurrence_pattern = models.CharField(max_length=100, blank=True, verbose_name="Tekrar Deseni", help_text="cron formatı")
    
    # Parametreler
    parameters = models.JSONField(default=dict, blank=True, verbose_name="Parametreler")
    
    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    
    # Sonuç
    result = models.TextField(blank=True, verbose_name="Sonuç")
    error_message = models.TextField(blank=True, verbose_name="Hata Mesajı")
    
    # Çalışma bilgisi
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Başlangıç")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş")
    execution_time_ms = models.IntegerField(null=True, blank=True, verbose_name="Çalışma Süresi (ms)")
    
    # İlişki
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_tasks', verbose_name="Oluşturan")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Zamanlanmış Görev"
        verbose_name_plural = "Zamanlanmış Görevler"
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['task_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.scheduled_at}"


class SupportTicket(models.Model):
    """
    Kullanıcı destek talepleri
    """
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('normal', 'Normal'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Açık'),
        ('in_progress', 'İşleniyor'),
        ('waiting_user', 'Kullanıcı Yanıtı Bekleniyor'),
        ('resolved', 'Çözüldü'),
        ('closed', 'Kapatıldı'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets',
        verbose_name="Kullanıcı"
    )
    
    subject = models.CharField(max_length=200, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name="Öncelik"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name="Durum"
    )
    
    # Atanan personel
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name="Atanan"
    )
    
    # Çözüm
    resolution = models.TextField(blank=True, verbose_name="Çözüm")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Çözüm Tarihi")
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")
    
    class Meta:
        verbose_name = "Destek Talebi"
        verbose_name_plural = "Destek Talepleri"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"#{self.id} - {self.subject} ({self.get_status_display()})"
    
    def get_priority_badge_class(self):
        """Öncelik badge rengi"""
        return {
            'low': 'secondary',
            'normal': 'info',
            'high': 'warning',
            'urgent': 'danger'
        }.get(self.priority, 'secondary')
    
    def get_status_badge_class(self):
        """Durum badge rengi"""
        return {
            'open': 'primary',
            'in_progress': 'warning',
            'waiting_user': 'info',
            'resolved': 'success',
            'closed': 'secondary'
        }.get(self.status, 'secondary')