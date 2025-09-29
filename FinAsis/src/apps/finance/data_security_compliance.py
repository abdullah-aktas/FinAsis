# -*- coding: utf-8 -*-
"""
FinAsis - Veri Güvenliği ve GDPR/KVKK Uyumluluk Modülleri
Kişisel verilerin korunması ve güvenli veri işleme
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.conf import settings as dj_settings
try:
    from cryptography.fernet import Fernet  # type: ignore
except Exception:  # pragma: no cover
    class Fernet:  # minimal stub fallback
        def __init__(self, *args, **kwargs):
            raise ImportError('cryptography paketi yüklü değil: pip install cryptography')
        @staticmethod
        def generate_key():  # basic stand-in
            return b'insecure-key'
import hashlib
import json
import uuid
from datetime import datetime, timedelta

from src.apps.accounting.models import Company


class PersonalDataCategory(models.Model):
    """
    Kişisel Veri Kategorileri (KVKK Uyumu)
    """
    
    SENSITIVITY_LEVELS = [
        ('PUBLIC', _('Genel')),
        ('INTERNAL', _('Dahili')),
        ('CONFIDENTIAL', _('Gizli')),
        ('RESTRICTED', _('Çok Gizli')),
        ('SENSITIVE', _('Hassas Kişisel Veri')),  # KVKK Özel Kategori
    ]
    
    PROCESSING_PURPOSES = [
        ('CONTRACTUAL', _('Sözleşme Gereği')),
        ('LEGAL_OBLIGATION', _('Yasal Yükümlülük')),
        ('LEGITIMATE_INTEREST', _('Meşru Menfaat')),
        ('CONSENT', _('Açık Rıza')),
        ('PUBLIC_INTEREST', _('Kamu Yararı')),
        ('VITAL_INTEREST', _('Yaşamsal Çıkar')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='data_categories')
    
    # Kategori bilgileri
    name = models.CharField(_('Kategori Adı'), max_length=100)
    description = models.TextField(_('Açıklama'))
    sensitivity_level = models.CharField(_('Hassasiyet Seviyesi'), max_length=20, choices=SENSITIVITY_LEVELS)
    
    # KVKK gereksinimleri
    processing_purpose = models.CharField(_('İşleme Amacı'), max_length=20, choices=PROCESSING_PURPOSES)
    legal_basis = models.TextField(_('Hukuki Dayanak'), 
                                  help_text="KVKK'nın hangi maddesi veya başka yasal düzenleme")
    
    # Saklama süresi
    retention_period_months = models.PositiveIntegerField(_('Saklama Süresi (Ay)'), 
                                                        help_text="0 = Süresiz")
    deletion_required = models.BooleanField(_('Otomatik Silme Gerekli'), default=True)
    
    # Veri sahipleri bilgilendirildi mi?
    data_subjects_informed = models.BooleanField(_('Veri Sahipleri Bilgilendirildi'), default=False)
    information_method = models.CharField(_('Bilgilendirme Yöntemi'), max_length=100, blank=True,
                                        help_text="E-posta, SMS, Web sitesi aydınlatma metni vb.")
    
    # Güvenlik önlemleri
    encryption_required = models.BooleanField(_('Şifreleme Gerekli'), default=False)
    access_restrictions = models.JSONField(_('Erişim Kısıtları'), default=list, blank=True,
                                         help_text="Hangi roller/departmanlar erişebilir")
    
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Kişisel Veri Kategorisi')
        verbose_name_plural = _('Kişisel Veri Kategorileri')
        ordering = ['name']
        
    def __str__(self):
        display = getattr(self, 'get_sensitivity_level_display', lambda: '')()
        return f"{self.name} ({display})"
    
    def get_retention_end_date(self, creation_date=None):
        """Saklama süresinin bitiş tarihini hesapla"""
        if self.retention_period_months == 0:  # Süresiz
            return None
            
        if not creation_date:
            creation_date = timezone.now().date()
            
        end_date = creation_date + timedelta(days=self.retention_period_months * 30)
        return end_date


class PersonalDataRecord(models.Model):
    """
    Kişisel Veri Kaydı İzleme
    Her kişisel veri işleme faaliyetinin kaydı
    """
    
    PROCESSING_ACTIVITIES = [
        ('COLLECTION', _('Toplama')),
        ('STORAGE', _('Saklama')),
        ('UPDATE', _('Güncelleme')),
        ('SHARING', _('Paylaşma')),
        ('TRANSFER', _('Aktarma')),
        ('ANONYMIZATION', _('Anonimleştirme')),
        ('DELETION', _('Silme')),
        ('ACCESS', _('Erişim')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='personal_data_records')
    data_category = models.ForeignKey(PersonalDataCategory, on_delete=models.PROTECT, 
                                    related_name='data_records', verbose_name=_('Veri Kategorisi'))
    
    # Veri sahibi bilgileri
    data_subject_id = models.CharField(_('Veri Sahibi ID'), max_length=100,
                                     help_text="Müşteri ID, çalışan ID vb. (hashlenmiş)")
    data_subject_type = models.CharField(_('Veri Sahibi Tipi'), max_length=50,
                                       help_text="customer, employee, vendor vb.")
    
    # İşleme faaliyeti
    processing_activity = models.CharField(_('İşleme Faaliyeti'), max_length=20, choices=PROCESSING_ACTIVITIES)
    processing_date = models.DateTimeField(_('İşleme Tarihi'), auto_now_add=True)
    processed_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('İşleyen Kişi'))
    
    # İşleme detayları
    data_fields_processed = models.JSONField(_('İşlenen Veri Alanları'), default=list,
                                           help_text="Hangi alanlar işlendi: name, email, phone vb.")
    processing_purpose = models.TextField(_('İşleme Amacı'))
    
    # Hukuki dayanak
    consent_obtained = models.BooleanField(_('Rıza Alındı'), default=False)
    consent_date = models.DateTimeField(_('Rıza Tarihi'), null=True, blank=True)
    consent_method = models.CharField(_('Rıza Yöntemi'), max_length=100, blank=True,
                                    help_text="Online form, yazılı belge vb.")
    
    # Güvenlik
    ip_address = models.GenericIPAddressField(_('IP Adresi'), null=True, blank=True)
    user_agent = models.TextField(_('Kullanıcı Aracısı'), blank=True)
    
    # İlgili sistem kaydı
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Silme bilgileri
    scheduled_deletion_date = models.DateField(_('Planlanan Silme Tarihi'), null=True, blank=True)
    is_deleted = models.BooleanField(_('Silindi'), default=False)
    deletion_date = models.DateTimeField(_('Silme Tarihi'), null=True, blank=True)
    deletion_method = models.CharField(_('Silme Yöntemi'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('Kişisel Veri Kaydı')
        verbose_name_plural = _('Kişisel Veri Kayıtları')
        ordering = ['-processing_date']
        indexes = [
            models.Index(fields=['data_subject_id', 'data_subject_type']),
            models.Index(fields=['processing_activity', 'processing_date']),
            models.Index(fields=['scheduled_deletion_date']),
        ]
        
    def __str__(self):
        act = getattr(self, 'get_processing_activity_display', lambda: '')()
        return f"{self.data_subject_id} - {act} ({self.processing_date})"
    
    def calculate_deletion_date(self):
        """Silme tarihini hesapla ve planla"""
        if self.data_category.retention_period_months == 0:
            return None  # Süresiz saklama
            
        deletion_date = self.processing_date.date() + timedelta(
            days=self.data_category.retention_period_months * 30
        )
        self.scheduled_deletion_date = deletion_date
        self.save(update_fields=['scheduled_deletion_date'])
        return deletion_date
    
    def mark_for_deletion(self):
        """Silinmek üzere işaretle"""
        self.scheduled_deletion_date = timezone.now().date()
        self.save(update_fields=['scheduled_deletion_date'])
    
    def execute_deletion(self, method='AUTOMATIC'):
        """Silme işlemini gerçekleştir"""
        self.is_deleted = True
        self.deletion_date = timezone.now()
        self.deletion_method = method
        self.save(update_fields=['is_deleted', 'deletion_date', 'deletion_method'])


class DataSubjectRequest(models.Model):
    """
    Veri Sahibi Talepleri (KVKK m.11)
    Erişim, düzeltme, silme, itiraz vb. haklar
    """
    
    REQUEST_TYPES = [
        ('ACCESS', _('Erişim Hakkı')),  # KVKK m.11/1-a
        ('RECTIFICATION', _('Düzeltme Hakkı')),  # KVKK m.11/1-b
        ('ERASURE', _('Silme Hakkı')),  # KVKK m.11/1-c
        ('OBJECTION', _('İtiraz Hakkı')),  # KVKK m.11/1-d
        ('PORTABILITY', _('Taşınabilirlik Hakkı')),  # KVKK m.11/1-e
        ('RESTRICTION', _('İşleme Kısıtlama Hakkı')),
        ('COMPLAINT', _('Şikayet')),
    ]
    
    STATUS_CHOICES = [
        ('RECEIVED', _('Alındı')),
        ('UNDER_REVIEW', _('İnceleniyor')),
        ('ADDITIONAL_INFO_REQUIRED', _('Ek Bilgi Gerekli')),
        ('APPROVED', _('Onaylandı')),
        ('PARTIALLY_APPROVED', _('Kısmen Onaylandı')),
        ('REJECTED', _('Reddedildi')),
        ('COMPLETED', _('Tamamlandı')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='data_subject_requests')
    
    # Talep bilgileri
    request_id = models.UUIDField(_('Talep ID'), default=uuid.uuid4, unique=True)
    request_type = models.CharField(_('Talep Tipi'), max_length=20, choices=REQUEST_TYPES)
    request_date = models.DateTimeField(_('Talep Tarihi'), auto_now_add=True)
    
    # Veri sahibi bilgileri
    data_subject_name = models.CharField(_('Ad Soyad'), max_length=200)
    data_subject_email = models.EmailField(_('E-posta'))
    data_subject_phone = models.CharField(_('Telefon'), max_length=20, blank=True)
    identity_verified = models.BooleanField(_('Kimlik Doğrulandı'), default=False)
    verification_method = models.CharField(_('Doğrulama Yöntemi'), max_length=100, blank=True)
    
    # Talep detayları
    request_description = models.TextField(_('Talep Açıklaması'))
    specific_data_requested = models.JSONField(_('Talep Edilen Belirli Veriler'), default=list, blank=True)
    preferred_response_method = models.CharField(_('Tercih Edilen Yanıt Yöntemi'), max_length=50, 
                                               choices=[
                                                   ('EMAIL', _('E-posta')),
                                                   ('POST', _('Posta')),
                                                   ('PHONE', _('Telefon')),
                                                   ('IN_PERSON', _('Şahsen')),
                                               ], default='EMAIL')
    
    # İşlem durumu
    status = models.CharField(_('Durum'), max_length=30, choices=STATUS_CHOICES, default='RECEIVED')
    assigned_to = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name=_('Atanan Kişi'))
    
    # Süre takibi (KVKK: En geç 30 gün içinde yanıtlanmalı)
    due_date = models.DateTimeField(_('Vade Tarihi'), null=True, blank=True)
    response_date = models.DateTimeField(_('Yanıt Tarihi'), null=True, blank=True)
    is_overdue = models.BooleanField(_('Süresi Geçti'), default=False)
    
    # Yanıt bilgileri
    response_summary = models.TextField(_('Yanıt Özeti'), blank=True)
    rejection_reason = models.TextField(_('Red Gerekçesi'), blank=True)
    actions_taken = models.JSONField(_('Alınan Aksiyonlar'), default=list, blank=True)
    
    # Ek bilgiler
    supporting_documents = models.JSONField(_('Destekleyici Belgeler'), default=list, blank=True)
    internal_notes = models.TextField(_('İç Notlar'), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Veri Sahibi Talebi')
        verbose_name_plural = _('Veri Sahibi Talepleri')
        ordering = ['-request_date']
        
    def __str__(self):
        rtype = getattr(self, 'get_request_type_display', lambda: '')()
        return f"{self.request_id} - {self.data_subject_name} - {rtype}"
    
    def calculate_due_date(self):
        """Vade tarihini hesapla (KVKK: 30 gün)"""
        self.due_date = self.request_date + timedelta(days=30)
        self.save(update_fields=['due_date'])
    
    def check_overdue_status(self):
        """Vadesi geçmiş durumunu kontrol et"""
        if self.due_date and timezone.now() > self.due_date and self.status not in ['COMPLETED', 'REJECTED']:
            self.is_overdue = True
            self.save(update_fields=['is_overdue'])
    
    def complete_request(self, response_summary, actions_taken=None):
        """Talebi tamamla"""
        self.status = 'COMPLETED'
        self.response_date = timezone.now()
        self.response_summary = response_summary
        if actions_taken:
            self.actions_taken = actions_taken
        self.save()


class EncryptionKey(models.Model):
    """
    Şifreleme Anahtarları Yönetimi
    """
    
    KEY_TYPES = [
        ('AES', _('AES Şifreleme')),
        ('FERNET', _('Fernet Şifreleme')),
        ('RSA', _('RSA Şifreleme')),
        ('HASH', _('Hash Fonksiyonu')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='encryption_keys')
    
    # Anahtar bilgileri
    key_name = models.CharField(_('Anahtar Adı'), max_length=100)
    key_type = models.CharField(_('Anahtar Tipi'), max_length=20, choices=KEY_TYPES)
    key_purpose = models.CharField(_('Kullanım Amacı'), max_length=100,
                                  help_text="personal_data, financial_data, backups vb.")
    
    # Şifreleme parametreleri
    algorithm = models.CharField(_('Algoritma'), max_length=50)
    key_length = models.PositiveIntegerField(_('Anahtar Uzunluğu (bit)'))
    
    # Anahtar değeri (şifrelenmiş olarak saklanır)
    encrypted_key_value = models.BinaryField(_('Şifrelenmiş Anahtar Değeri'))
    key_hash = models.CharField(_('Anahtar Hash'), max_length=128, unique=True)
    
    # Anahtar yaşam döngüsü
    created_date = models.DateTimeField(_('Oluşturma Tarihi'), auto_now_add=True)
    activation_date = models.DateTimeField(_('Aktivasyon Tarihi'), default=timezone.now)
    expiration_date = models.DateTimeField(_('Son Kullanma Tarihi'), null=True, blank=True)
    
    # Durum
    is_active = models.BooleanField(_('Aktif'), default=True)
    is_compromised = models.BooleanField(_('Güvenliği İhlal Edildi'), default=False)
    rotation_required = models.BooleanField(_('Rotasyon Gerekli'), default=False)
    
    # Kullanım istatistikleri
    usage_count = models.PositiveIntegerField(_('Kullanım Sayısı'), default=0)
    last_used_date = models.DateTimeField(_('Son Kullanım Tarihi'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Şifreleme Anahtarı')
        verbose_name_plural = _('Şifreleme Anahtarları')
        ordering = ['-created_date']
        
    def __str__(self):
        return f"{self.key_name} ({self.key_type})"
    
    def generate_key_hash(self, key_value):
        """Anahtar hash değerini oluştur"""
        return hashlib.sha256(key_value.encode()).hexdigest()
    
    def is_expired(self):
        """Anahtarın süresi dolmuş mu?"""
        if not self.expiration_date:
            return False
        return timezone.now() > self.expiration_date
    
    def increment_usage(self):
        """Kullanım sayısını artır"""
        self.usage_count += 1
        self.last_used_date = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_date'])


class DataEncryption(models.Model):
    """
    Veri Şifreleme Kayıtları
    Hangi verilerin ne zaman şifrelendiğini takip eder
    """
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='data_encryptions')
    encryption_key = models.ForeignKey(EncryptionKey, on_delete=models.PROTECT, 
                                     related_name='encrypted_data', verbose_name=_('Şifreleme Anahtarı'))
    
    # Şifrelenen veri bilgileri
    data_identifier = models.CharField(_('Veri Tanımlayıcısı'), max_length=255,
                                     help_text="Tablo adı, alan adı, kayıt ID'si vb.")
    data_type = models.CharField(_('Veri Tipi'), max_length=100,
                               help_text="personal_data, financial_record, document vb.")
    
    # İlgili sistem kaydı
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Şifreleme bilgileri
    encryption_date = models.DateTimeField(_('Şifreleme Tarihi'), auto_now_add=True)
    encrypted_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   verbose_name=_('Şifreleyen'))
    
    # Hash değeri (veri bütünlüğü kontrolü için)
    data_hash = models.CharField(_('Veri Hash'), max_length=128)
    
    # Durum
    is_active = models.BooleanField(_('Aktif'), default=True)
    decryption_date = models.DateTimeField(_('Şifre Çözme Tarihi'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Veri Şifreleme Kaydı')
        verbose_name_plural = _('Veri Şifreleme Kayıtları')
        ordering = ['-encryption_date']
        indexes = [
            models.Index(fields=['data_identifier', 'data_type']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        
    def __str__(self):
        return f"{self.data_identifier} - {self.encryption_date}"


class DataBackup(models.Model):
    """
    Veri Yedekleme Kayıtları
    """
    
    BACKUP_TYPES = [
        ('FULL', _('Tam Yedek')),
        ('INCREMENTAL', _('Artan Yedek')),
        ('DIFFERENTIAL', _('Fark Yedek')),
        ('SELECTIVE', _('Seçici Yedek')),
    ]
    
    BACKUP_STATUS = [
        ('IN_PROGRESS', _('Devam Ediyor')),
        ('COMPLETED', _('Tamamlandı')),
        ('FAILED', _('Başarısız')),
        ('CORRUPTED', _('Bozuk')),
        ('VERIFIED', _('Doğrulandı')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='data_backups')
    
    # Yedek bilgileri
    backup_name = models.CharField(_('Yedek Adı'), max_length=200)
    backup_type = models.CharField(_('Yedek Tipi'), max_length=20, choices=BACKUP_TYPES)
    backup_date = models.DateTimeField(_('Yedekleme Tarihi'), auto_now_add=True)
    
    # İçerik bilgileri
    included_tables = models.JSONField(_('Dahil Edilen Tablolar'), default=list)
    excluded_tables = models.JSONField(_('Hariç Tutulan Tablolar'), default=list, blank=True)
    record_count = models.PositiveBigIntegerField(_('Kayıt Sayısı'), default=0)
    
    # Dosya bilgileri
    file_path = models.CharField(_('Dosya Yolu'), max_length=500)
    file_size_bytes = models.PositiveBigIntegerField(_('Dosya Boyutu (Byte)'), default=0)
    compression_used = models.BooleanField(_('Sıkıştırma Kullanıldı'), default=True)
    encryption_used = models.BooleanField(_('Şifreleme Kullanıldı'), default=True)
    
    # Bütünlük kontrolü
    file_hash = models.CharField(_('Dosya Hash'), max_length=128)
    checksum = models.CharField(_('Checksum'), max_length=128, blank=True)
    
    # Durum ve süre
    status = models.CharField(_('Durum'), max_length=20, choices=BACKUP_STATUS, default='IN_PROGRESS')
    start_time = models.DateTimeField(_('Başlangıç Zamanı'))
    end_time = models.DateTimeField(_('Bitiş Zamanı'), null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(_('Süre (Saniye)'), null=True, blank=True)
    
    # Saklama bilgileri
    retention_period_days = models.PositiveIntegerField(_('Saklama Süresi (Gün)'), default=365)
    scheduled_deletion_date = models.DateTimeField(_('Planlanan Silme Tarihi'), null=True, blank=True)
    
    # Doğrulama
    last_verification_date = models.DateTimeField(_('Son Doğrulama Tarihi'), null=True, blank=True)
    verification_status = models.CharField(_('Doğrulama Durumu'), max_length=20, choices=[
        ('NOT_VERIFIED', _('Doğrulanmadı')),
        ('VERIFIED', _('Doğrulandı')),
        ('VERIFICATION_FAILED', _('Doğrulama Başarısız')),
    ], default='NOT_VERIFIED')
    
    # Hata bilgileri
    error_message = models.TextField(_('Hata Mesajı'), blank=True)
    
    created_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                 verbose_name=_('Oluşturan'))
    
    class Meta:
        verbose_name = _('Veri Yedek')
        verbose_name_plural = _('Veri Yedekleri')
        ordering = ['-backup_date']
        
    def __str__(self):
        return f"{self.backup_name} - {self.backup_date.strftime('%Y-%m-%d %H:%M')}"
    
    def calculate_deletion_date(self):
        """Silme tarihini hesapla"""
        if self.backup_date:
            self.scheduled_deletion_date = self.backup_date + timedelta(days=self.retention_period_days)
            self.save(update_fields=['scheduled_deletion_date'])
    
    def verify_integrity(self):
        """Yedek bütünlüğünü doğrula"""
        import os
        import hashlib
        
        if not os.path.exists(self.file_path):
            self.verification_status = 'VERIFICATION_FAILED'
            self.error_message = 'Yedek dosyası bulunamadı'
            self.save()
            return False
        
        # Dosya hash'ini yeniden hesapla
        hasher = hashlib.sha256()
        with open(self.file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        current_hash = hasher.hexdigest()
        
        if current_hash == self.file_hash:
            self.verification_status = 'VERIFIED'
            self.last_verification_date = timezone.now()
            self.error_message = ''
        else:
            self.verification_status = 'VERIFICATION_FAILED'
            self.error_message = 'Dosya hash değeri eşleşmiyor - dosya bozulmuş olabilir'
        
        self.save()
        return self.verification_status == 'VERIFIED'


class SecurityIncident(models.Model):
    """
    Güvenlik Olayları Kayıt ve Takip Sistemi
    """
    
    INCIDENT_TYPES = [
        ('DATA_BREACH', _('Veri İhlali')),
        ('UNAUTHORIZED_ACCESS', _('Yetkisiz Erişim')),
        ('MALWARE', _('Zararlı Yazılım')),
        ('PHISHING', _('Kimlik Avı')),
        ('SYSTEM_COMPROMISE', _('Sistem Güvenliği İhlali')),
        ('PHYSICAL_BREACH', _('Fiziksel Güvenlik İhlali')),
        ('INSIDER_THREAT', _('İç Tehdit')),
        ('DDoS', _('Hizmet Dışı Bırakma Saldırısı')),
        ('OTHER', _('Diğer')),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', _('Düşük')),
        ('MEDIUM', _('Orta')),
        ('HIGH', _('Yüksek')),
        ('CRITICAL', _('Kritik')),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', _('Açık')),
        ('INVESTIGATING', _('Araştırılıyor')),
        ('CONTAINED', _('Kontrol Altına Alındı')),
        ('RESOLVED', _('Çözümlendi')),
        ('CLOSED', _('Kapatıldı')),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='security_incidents')
    
    # Olay bilgileri
    incident_id = models.UUIDField(_('Olay ID'), default=uuid.uuid4, unique=True)
    incident_type = models.CharField(_('Olay Tipi'), max_length=30, choices=INCIDENT_TYPES)
    title = models.CharField(_('Başlık'), max_length=200)
    description = models.TextField(_('Açıklama'))
    
    # Zaman bilgileri
    detected_date = models.DateTimeField(_('Tespit Tarihi'))
    occurred_date = models.DateTimeField(_('Gerçekleşme Tarihi'), null=True, blank=True)
    reported_date = models.DateTimeField(_('Raporlama Tarihi'), auto_now_add=True)
    
    # Şiddet ve etki
    severity = models.CharField(_('Şiddet'), max_length=20, choices=SEVERITY_LEVELS)
    affected_systems = models.JSONField(_('Etkilenen Sistemler'), default=list)
    affected_data_types = models.JSONField(_('Etkilenen Veri Tipleri'), default=list)
    estimated_records_affected = models.PositiveIntegerField(_('Etkilenen Kayıt Sayısı (Tahmini)'), 
                                                          null=True, blank=True)
    
    # Veri ihlali detayları (KVKK Uyumu)
    is_personal_data_involved = models.BooleanField(_('Kişisel Veri İçeriyor'), default=False)
    personal_data_categories = models.JSONField(_('Etkilenen Kişisel Veri Kategorileri'), default=list, blank=True)
    data_subjects_affected = models.PositiveIntegerField(_('Etkilenen Veri Sahibi Sayısı'), 
                                                       null=True, blank=True)
    
    # Bildirimi gerekli mi? (KVKK m.12: 72 saat içinde VVK'ya bildirim)
    kvkk_notification_required = models.BooleanField(_('KVKK Bildirimi Gerekli'), default=False)
    kvkk_notification_sent = models.BooleanField(_('KVKK Bildirimi Gönderildi'), default=False)
    kvkk_notification_date = models.DateTimeField(_('KVKK Bildirim Tarihi'), null=True, blank=True)
    
    # Veri sahipleri bilgilendirildi mi?
    data_subjects_notification_required = models.BooleanField(_('Veri Sahipleri Bildirimi Gerekli'), default=False)
    data_subjects_notification_sent = models.BooleanField(_('Veri Sahipleri Bildirimi Gönderildi'), default=False)
    data_subjects_notification_date = models.DateTimeField(_('Veri Sahipleri Bildirim Tarihi'), 
                                                          null=True, blank=True)
    
    # Durum takibi
    status = models.CharField(_('Durum'), max_length=20, choices=STATUS_CHOICES, default='OPEN')
    assigned_to = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name=_('Atanan Kişi'))
    
    # Çözüm bilgileri
    root_cause = models.TextField(_('Kök Neden'), blank=True)
    resolution_summary = models.TextField(_('Çözüm Özeti'), blank=True)
    lessons_learned = models.TextField(_('Alınan Dersler'), blank=True)
    
    # Müdahale süresi
    response_time_hours = models.DecimalField(_('Müdahale Süresi (Saat)'), max_digits=8, decimal_places=2, 
                                           null=True, blank=True)
    resolution_time_hours = models.DecimalField(_('Çözüm Süresi (Saat)'), max_digits=8, decimal_places=2, 
                                             null=True, blank=True)
    
    # Mali etki
    estimated_cost = models.DecimalField(_('Tahmini Maliyet'), max_digits=15, decimal_places=2, 
                                       null=True, blank=True)
    actual_cost = models.DecimalField(_('Gerçek Maliyet'), max_digits=15, decimal_places=2, 
                                    null=True, blank=True)
    
    # Raporlama
    reported_by = models.ForeignKey(dj_settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  related_name='reported_incidents', verbose_name=_('Raporlayan'))
    external_authorities_notified = models.JSONField(_('Bilgilendirilen Dış Otoriteler'), default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Güvenlik Olayı')
        verbose_name_plural = _('Güvenlik Olayları')
        ordering = ['-detected_date']
        
    def __str__(self):
        sev = getattr(self, 'get_severity_display', lambda: '')()
        return f"{self.incident_id} - {self.title} ({sev})"
    
    def calculate_response_time(self):
        """Müdahale süresini hesapla"""
        if self.status in ['INVESTIGATING', 'CONTAINED', 'RESOLVED', 'CLOSED']:
            # İlk müdahale zamanını bul (status değişiklik kaydından)
            # Bu örnekte basit hesaplama yapıyoruz
            hours = (timezone.now() - self.detected_date).total_seconds() / 3600
            self.response_time_hours = round(hours, 2)
            self.save(update_fields=['response_time_hours'])
    
    def check_kvkk_notification_deadline(self):
        """KVKK bildirim süresini kontrol et (72 saat)"""
        if not self.is_personal_data_involved or self.kvkk_notification_sent:
            return True
            
        deadline = self.detected_date + timedelta(hours=72)
        return timezone.now() <= deadline
    
    def is_kvkk_notification_overdue(self):
        """KVKK bildirim süresi geçti mi?"""
        if not self.is_personal_data_involved or self.kvkk_notification_sent:
            return False
            
        deadline = self.detected_date + timedelta(hours=72)
        return timezone.now() > deadline


# Yardımcı servisler ve fonksiyonlar
class GDPRComplianceChecker:
    """GDPR/KVKK Uyumluluk Kontrolcüsü"""
    
    def __init__(self, company):
        self.company = company
    
    def check_data_retention_compliance(self):
        """Veri saklama süresi uyumluluğunu kontrol et"""
        overdue_records = PersonalDataRecord.objects.filter(
            company=self.company,
            scheduled_deletion_date__lt=timezone.now().date(),
            is_deleted=False
        )
        
        return {
            'overdue_count': overdue_records.count(),
            'overdue_records': list(overdue_records.values('id', 'data_subject_id', 'scheduled_deletion_date')),
            'compliance_status': 'NON_COMPLIANT' if overdue_records.exists() else 'COMPLIANT'
        }
    
    def check_consent_validity(self):
        """Rıza geçerliliğini kontrol et"""
        # 2 yıldan eski rızalar yenilenmeli
        old_consents = PersonalDataRecord.objects.filter(
            company=self.company,
            consent_obtained=True,
            consent_date__lt=timezone.now() - timedelta(days=730),
            is_deleted=False
        )
        
        return {
            'old_consent_count': old_consents.count(),
            'renewal_required': old_consents.exists()
        }
    
    def check_data_subject_requests_compliance(self):
        """Veri sahibi talepleri uyumluluğunu kontrol et"""
        overdue_requests = DataSubjectRequest.objects.filter(
            company=self.company,
            is_overdue=True,
            status__in=['RECEIVED', 'UNDER_REVIEW', 'IN_PROGRESS']
        )
        
        return {
            'overdue_requests': overdue_requests.count(),
            'average_response_time': self._calculate_average_response_time(),
            'compliance_rate': self._calculate_compliance_rate()
        }
    
    def generate_compliance_report(self):
        """Genel uyumluluk raporu oluştur"""
        retention_check = self.check_data_retention_compliance()
        consent_check = self.check_consent_validity()
        requests_check = self.check_data_subject_requests_compliance()
        
        # Güvenlik olayları kontrolü
        recent_incidents = SecurityIncident.objects.filter(
            company=self.company,
            is_personal_data_involved=True,
            detected_date__gte=timezone.now() - timedelta(days=30)
        )
        
        overdue_kvkk_notifications = recent_incidents.filter(
            kvkk_notification_required=True,
            kvkk_notification_sent=False,
            detected_date__lt=timezone.now() - timedelta(hours=72)
        )
        
        overall_score = self._calculate_compliance_score(
            retention_check, consent_check, requests_check, overdue_kvkk_notifications.count()
        )
        
        return {
            'company': self.company.name,
            'report_date': timezone.now(),
            'overall_compliance_score': overall_score,
            'data_retention_compliance': retention_check,
            'consent_management': consent_check,
            'data_subject_requests': requests_check,
            'security_incidents': {
                'recent_incidents_count': recent_incidents.count(),
                'overdue_kvkk_notifications': overdue_kvkk_notifications.count()
            },
            'recommendations': self._generate_recommendations(retention_check, consent_check, requests_check)
        }
    
    def _calculate_average_response_time(self):
        """Ortalama yanıt süresini hesapla"""
        completed_requests = DataSubjectRequest.objects.filter(
            company=self.company,
            response_date__isnull=False
        )
        
        if not completed_requests.exists():
            return 0
        
        total_hours = 0
        for request in completed_requests:
            req_date = getattr(request, 'request_date', None)
            resp_date = getattr(request, 'response_date', None)
            if req_date and resp_date:
                duration = resp_date - req_date
                total_hours += duration.total_seconds() / 3600
        
        return round(total_hours / completed_requests.count(), 2)
    
    def _calculate_compliance_rate(self):
        """Uyum oranını hesapla"""
        all_requests = DataSubjectRequest.objects.filter(company=self.company)
        if not all_requests.exists():
            return 100
        
        compliant_requests = all_requests.exclude(is_overdue=True)
        return round((compliant_requests.count() / all_requests.count()) * 100, 2)
    
    def _calculate_compliance_score(self, retention_check, consent_check, requests_check, overdue_notifications):
        """Genel uyumluluk skorunu hesapla (0-100)"""
        score = 100
        
        # Veri saklama uyumsuzlukları
        if retention_check['overdue_count'] > 0:
            score -= min(30, retention_check['overdue_count'] * 2)
        
        # Eski rızalar
        if consent_check['renewal_required']:
            score -= 15
        
        # Geç yanıtlanan talepler
        if requests_check['overdue_requests'] > 0:
            score -= min(25, requests_check['overdue_requests'] * 5)
        
        # KVKK bildirim gecikmeleri
        if overdue_notifications > 0:
            score -= min(30, overdue_notifications * 15)
        
        return max(0, score)
    
    def _generate_recommendations(self, retention_check, consent_check, requests_check):
        """Önerileri oluştur"""
        recommendations = []
        
        if retention_check['overdue_count'] > 0:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Veri Saklama Süresi Aşımı',
                'description': f"{retention_check['overdue_count']} adet kayıt saklama süresini aştı.",
                'action': 'Süresi geçen kişisel verileri derhal silin veya anonimleştirin.'
            })
        
        if consent_check['renewal_required']:
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Rıza Yenileme Gerekli',
                'description': 'Eski tarihli rızalar bulundu.',
                'action': 'İlgili veri sahiplerinden rıza yenilemesi talep edin.'
            })
        
        if requests_check['overdue_requests'] > 0:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Geciken Veri Sahibi Talepleri',
                'description': f"{requests_check['overdue_requests']} adet talep süresi içinde yanıtlanmadı.",
                'action': 'Geciken talepleri öncelikli olarak değerlendirin ve yanıtlayın.'
            })
        
        return recommendations