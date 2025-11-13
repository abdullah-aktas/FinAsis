from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# ============================================================================
# ÇOK DİLLİ İÇERİK YÖNETİMİ MODELLERİ
# ============================================================================

class Language(models.Model):
    """Desteklenen diller"""
    
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Dil Kodu"), help_text="tr, en, ar, ku, de, fr")
    name = models.CharField(max_length=100, verbose_name=_("Dil Adı"))
    native_name = models.CharField(max_length=100, verbose_name=_("Yerel Adı"))
    flag_emoji = models.CharField(max_length=10, blank=True, verbose_name=_("Bayrak Emoji"))
    
    # RTL desteği
    is_rtl = models.BooleanField(default=False, verbose_name=_("Sağdan Sola"))
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name=_("Aktif"))
    is_default = models.BooleanField(default=False, verbose_name=_("Varsayılan"))
    
    # Sıralama
    order = models.IntegerField(default=0, verbose_name=_("Sıra"))
    
    # İstatistikler
    translation_completeness = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("Çeviri Tamamlanma %"))
    total_strings = models.IntegerField(default=0, verbose_name=_("Toplam String"))
    translated_strings = models.IntegerField(default=0, verbose_name=_("Çevrilmiş String"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Dil")
        verbose_name_plural = _("Diller")
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.native_name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Sadece bir varsayılan dil olabilir
        if self.is_default:
            Language.objects.filter(is_default=True).update(is_default=False)
        
        # Tamamlanma yüzdesini hesapla
        if self.total_strings > 0:
            self.translation_completeness = (self.translated_strings / self.total_strings) * 100
        
        super().save(*args, **kwargs)


class TranslationString(models.Model):
    """Çeviri stringleri - key-value çeviri yönetimi"""
    
    CONTEXT_CHOICES = [
        ('UI', _('Kullanıcı Arayüzü')),
        ('EMAIL', _('E-posta')),
        ('SMS', _('SMS')),
        ('NOTIFICATION', _('Bildirim')),
        ('REPORT', _('Rapor')),
        ('ERROR', _('Hata Mesajı')),
        ('HELP', _('Yardım')),
    ]
    
    # Anahtar
    key = models.CharField(max_length=200, unique=True, verbose_name=_("Çeviri Anahtarı"), help_text="common.save, auth.login")
    context = models.CharField(max_length=20, choices=CONTEXT_CHOICES, default='UI', verbose_name=_("Bağlam"))
    
    # Kaynak metin
    source_text = models.TextField(verbose_name=_("Kaynak Metin (TR)"))
    
    # Metadata
    module = models.CharField(max_length=50, blank=True, verbose_name=_("Modül"))
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))
    
    # Değişkenler
    variables = models.JSONField(default=list, blank=True, verbose_name=_("Değişkenler"), help_text="['user', 'amount', ...]")
    
    # Durum
    is_translated = models.BooleanField(default=False, verbose_name=_("Çevrildi"))
    requires_review = models.BooleanField(default=False, verbose_name=_("İnceleme Gerekli"))
    
    # Kullanım
    usage_count = models.IntegerField(default=0, verbose_name=_("Kullanım Sayısı"))
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Son Kullanım"))
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Oluşturan"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Çeviri String")
        verbose_name_plural = _("Çeviri Stringler")
        ordering = ['module', 'key']
    
    def __str__(self):
        return f"{self.key}: {self.source_text[:50]}"


class Translation(models.Model):
    """Çeviriler - her dil için çeviri"""
    
    STATUS_CHOICES = [
        ('PENDING', _('Beklemede')),
        ('DRAFT', _('Taslak')),
        ('REVIEW', _('İncelemede')),
        ('APPROVED', _('Onaylandı')),
    ]
    
    translation_string = models.ForeignKey(TranslationString, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Çeviri String"))
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Dil"))
    
    # Çeviri
    translated_text = models.TextField(verbose_name=_("Çevrilmiş Metin"))
    
    # Durum
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name=_("Durum"))
    
    # Kalite
    is_machine_translated = models.BooleanField(default=False, verbose_name=_("Makine Çevirisi"))
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Güven Skoru"))
    
    # Review
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_translations', verbose_name=_("İnceleyen"))
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("İnceleme Tarihi"))
    
    # Metadata
    translated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Çeviren"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Çeviri")
        verbose_name_plural = _("Çeviriler")
        ordering = ['translation_string', 'language']
        unique_together = ['translation_string', 'language']
    
    def __str__(self):
        return f"{self.translation_string.key} [{self.language.code}]"


class LocalizedContent(models.Model):
    """Yerelleştirilmiş içerik - dinamik içerik çevirisi"""
    
    # Generic relation - herhangi bir modele bağlanabilir
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=64)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name=_("Dil"))
    
    # Alan çevirileri (JSON)
    field_name = models.CharField(max_length=100, verbose_name=_("Alan Adı"))
    translated_value = models.TextField(verbose_name=_("Çevrilmiş Değer"))
    
    # Durum
    is_published = models.BooleanField(default=False, verbose_name=_("Yayınlandı"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Yerelleştirilmiş İçerik")
        verbose_name_plural = _("Yerelleştirilmiş İçerikler")
        ordering = ['content_type', 'object_id', 'language']
        unique_together = ['content_type', 'object_id', 'language', 'field_name']
    
    def __str__(self):
        return f"{self.content_type} #{self.object_id} - {self.language.code} - {self.field_name}"


class TranslationMemory(models.Model):
    """Çeviri hafızası - daha önce yapılan çeviriler"""
    
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_memories', verbose_name=_("Kaynak Dil"))
    target_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='target_memories', verbose_name=_("Hedef Dil"))
    
    source_text = models.TextField(verbose_name=_("Kaynak Metin"))
    target_text = models.TextField(verbose_name=_("Hedef Metin"))
    
    # Kullanım
    usage_count = models.IntegerField(default=0, verbose_name=_("Kullanım Sayısı"))
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Son Kullanım"))
    
    # Kalite
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Kalite Skoru"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Doğrulandı"))
    
    # Metadata
    domain = models.CharField(max_length=50, blank=True, verbose_name=_("Alan"), help_text="finance, accounting, legal")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Çeviri Hafızası")
        verbose_name_plural = _("Çeviri Hafızaları")
        ordering = ['-usage_count', '-created_at']
    
    def __str__(self):
        return f"{self.source_language.code} → {self.target_language.code}: {self.source_text[:50]}"


class UserLanguagePreference(models.Model):
    """Kullanıcı dil tercihleri"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='language_preference', verbose_name=_("Kullanıcı"))
    preferred_language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, verbose_name=_("Tercih Edilen Dil"))
    
    # Fallback diller
    fallback_languages = models.JSONField(default=list, blank=True, verbose_name=_("Yedek Diller"))
    
    # Bölgesel ayarlar
    timezone = models.CharField(max_length=100, default='Europe/Istanbul', verbose_name=_("Zaman Dilimi"))
    date_format = models.CharField(max_length=50, default='DD.MM.YYYY', verbose_name=_("Tarih Formatı"))
    time_format = models.CharField(max_length=50, default='HH:mm', verbose_name=_("Saat Formatı"))
    number_format = models.CharField(max_length=50, default='1.234,56', verbose_name=_("Sayı Formatı"))
    currency_symbol = models.CharField(max_length=10, default='₺', verbose_name=_("Para Birimi Sembolü"))
    
    # Auto-translate
    auto_translate = models.BooleanField(default=False, verbose_name=_("Otomatik Çeviri"))
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Kullanıcı Dil Tercihi")
        verbose_name_plural = _("Kullanıcı Dil Tercihleri")
    
    def __str__(self):
        return f"{self.user.username} - {self.preferred_language}"


class TranslationJob(models.Model):
    """Çeviri işleri - toplu çeviri yönetimi"""
    
    STATUS_CHOICES = [
        ('PENDING', _('Beklemede')),
        ('IN_PROGRESS', _('Devam Ediyor')),
        ('COMPLETED', _('Tamamlandı')),
        ('FAILED', _('Başarısız')),
        ('CANCELLED', _('İptal Edildi')),
    ]
    
    job_name = models.CharField(max_length=200, verbose_name=_("İş Adı"))
    description = models.TextField(blank=True, verbose_name=_("Açıklama"))
    
    # Diller
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_jobs', verbose_name=_("Kaynak Dil"))
    target_languages = models.ManyToManyField(Language, related_name='target_jobs', verbose_name=_("Hedef Diller"))
    
    # İçerik
    content_items = models.JSONField(default=list, verbose_name=_("İçerik Maddeleri"))
    
    # İlerleme
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name=_("Durum"))
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("İlerleme %"))
    
    total_items = models.IntegerField(default=0, verbose_name=_("Toplam Madde"))
    completed_items = models.IntegerField(default=0, verbose_name=_("Tamamlanan Madde"))
    
    # Zamanlama
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Başlangıç"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Bitiş"))
    
    # Atama
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='translation_jobs', verbose_name=_("Atanan"))
    
    # Sonuç
    result_summary = models.TextField(blank=True, verbose_name=_("Sonuç Özeti"))
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Oluşturan"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Çeviri İşi")
        verbose_name_plural = _("Çeviri İşleri")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.job_name} ({self.status})"


class LocaleAuditLog(models.Model):
    """Çeviri denetim logları"""
    
    ACTION_CHOICES = [
        ('CREATE', _('Oluşturuldu')),
        ('UPDATE', _('Güncellendi')),
        ('DELETE', _('Silindi')),
        ('APPROVE', _('Onaylandı')),
        ('REJECT', _('Reddedildi')),
        ('PUBLISH', _('Yayınlandı')),
    ]
    
    translation = models.ForeignKey(Translation, on_delete=models.CASCADE, related_name='audit_logs', verbose_name=_("Çeviri"))
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name=_("Aksiyon"))
    
    # Değişiklik
    old_value = models.TextField(blank=True, verbose_name=_("Eski Değer"))
    new_value = models.TextField(blank=True, verbose_name=_("Yeni Değer"))
    
    # Kullanıcı
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Kullanıcı"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Adresi"))
    
    # Yorum
    comment = models.TextField(blank=True, verbose_name=_("Yorum"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Çeviri Denetim Logu")
        verbose_name_plural = _("Çeviri Denetim Logları")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.translation} - {self.action} ({self.created_at})"


class MissingTranslation(models.Model):
    """Eksik çeviriler - otomatik tespit"""
    
    translation_string = models.ForeignKey(TranslationString, on_delete=models.CASCADE, related_name='missing_translations', verbose_name=_("Çeviri String"))
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name=_("Dil"))
    
    # Tespit
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Tespit Tarihi"))
    detected_in = models.CharField(max_length=200, blank=True, verbose_name=_("Tespit Edilen Yer"))
    
    # Öncelik
    priority = models.CharField(max_length=20, choices=[
        ('LOW', _('Düşük')),
        ('MEDIUM', _('Orta')),
        ('HIGH', _('Yüksek')),
        ('CRITICAL', _('Kritik')),
    ], default='MEDIUM', verbose_name=_("Öncelik"))
    
    # Durum
    is_resolved = models.BooleanField(default=False, verbose_name=_("Çözüldü"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Çözüm Tarihi"))
    
    class Meta:
        verbose_name = _("Eksik Çeviri")
        verbose_name_plural = _("Eksik Çeviriler")
        ordering = ['-priority', '-detected_at']
        unique_together = ['translation_string', 'language']
    
    def __str__(self):
        return f"{self.translation_string.key} - {self.language.code}"

