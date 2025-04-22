from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils import timezone

class AIModel(models.Model):
    """Yapay zeka modellerinin versiyonlarını ve performansını takip etmek için model"""
    MODEL_TYPES = [
        ('financial', _('Finansal Analiz')),
        ('recommendation', _('Öneri Sistemi')),
        ('chat', _('Sohbet Sistemi')),
        ('prediction', _('Tahmin Sistemi')),
    ]

    name = models.CharField(_('Model Adı'), max_length=100)
    model_type = models.CharField(_('Model Tipi'), max_length=20, choices=MODEL_TYPES)
    version = models.CharField(_('Versiyon'), max_length=20)
    description = models.TextField(_('Açıklama'), blank=True)
    accuracy = models.FloatField(_('Doğruluk Oranı'))
    parameters = models.JSONField(_('Model Parametreleri'), default=dict)
    last_trained = models.DateTimeField(_('Son Eğitim Tarihi'), auto_now=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('AI Model')
        verbose_name_plural = _('AI Modeller')
        ordering = ['-last_trained']

    def __str__(self):
        return f"{self.name} v{self.version}"

class UserInteraction(models.Model):
    """Kullanıcı etkileşimlerini takip etmek için model"""
    INTERACTION_TYPES = [
        ('chat', _('Sohbet')),
        ('analysis', _('Analiz')),
        ('recommendation', _('Öneri')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            verbose_name=_('Kullanıcı'), related_name='ai_interactions')
    interaction_type = models.CharField(_('Etkileşim Tipi'), max_length=20, choices=INTERACTION_TYPES)
    content = models.TextField(_('İçerik'))  # Kullanıcının gönderdiği içerik
    ai_response = models.TextField(_('AI Yanıtı'))  # AI'ın verdiği yanıt
    feedback = models.IntegerField(_('Geri Bildirim'), null=True, blank=True)  # 1-5 arası puanlama
    feedback_text = models.TextField(_('Geri Bildirim Metni'), blank=True)
    processing_time = models.FloatField(_('İşlem Süresi'), help_text=_('Saniye cinsinden'))
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Kullanıcı Etkileşimi')
        verbose_name_plural = _('Kullanıcı Etkileşimleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.created_at}"

class FinancialPrediction(models.Model):
    """Finansal tahminleri ve analizleri saklamak için model"""
    PREDICTION_TYPES = [
        ('market_trend', _('Piyasa Trendi')),
        ('stock_price', _('Hisse Fiyatı')),
        ('risk_analysis', _('Risk Analizi')),
        ('portfolio_optimization', _('Portföy Optimizasyonu')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            verbose_name=_('Kullanıcı'), related_name='financial_predictions')
    prediction_type = models.CharField(_('Tahmin Tipi'), max_length=50, choices=PREDICTION_TYPES)
    input_data = models.JSONField(_('Girdi Verileri'))
    prediction_result = models.TextField(_('Tahmin Sonucu'))  # AI'ın ürettiği tahmin sonucu
    confidence = models.FloatField(_('Güven Oranı'))
    model_version = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True,
                                    verbose_name=_('Kullanılan Model'))
    is_validated = models.BooleanField(_('Doğrulandı'), default=False)
    validation_notes = models.TextField(_('Doğrulama Notları'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Finansal Tahmin')
        verbose_name_plural = _('Finansal Tahminler')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.prediction_type} - {self.created_at}"

class AIFeedback(models.Model):
    """AI sisteminin performansını değerlendirmek için geri bildirim modeli"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name=_('Kullanıcı'), related_name='ai_feedback')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE,
                            verbose_name=_('AI Model'), related_name='feedback')
    rating = models.IntegerField(_('Değerlendirme'), help_text=_('1-5 arası puanlama'))
    comment = models.TextField(_('Yorum'), blank=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('AI Geri Bildirimi')
        verbose_name_plural = _('AI Geri Bildirimleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.model.name} - {self.rating}"

class FinancialReport(models.Model):
    """Finansal Raporlar"""
    REPORT_TYPES = [
        ('balance_sheet', 'Bilanço'),
        ('income_statement', 'Gelir Tablosu'),
        ('cash_flow', 'Nakit Akışı'),
        ('budget', 'Bütçe'),
        ('custom', 'Özel Rapor'),
    ]

    title = models.CharField(_('Rapor Başlığı'), max_length=255)
    report_type = models.CharField(_('Rapor Tipi'), max_length=20, choices=REPORT_TYPES)
    content = models.JSONField(_('Rapor İçeriği'))
    parameters = models.JSONField(_('Rapor Parametreleri'), default=dict)
    generated_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Finansal Rapor')
        verbose_name_plural = _('Finansal Raporlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

class AnomalyDetection(models.Model):
    """Anomali Tespiti"""
    DETECTION_TYPES = [
        ('transaction', 'İşlem Anomalisi'),
        ('pattern', 'Örüntü Anomalisi'),
        ('trend', 'Trend Anomalisi'),
    ]

    detection_type = models.CharField(_('Tespit Tipi'), max_length=20, choices=DETECTION_TYPES)
    source_data = models.JSONField(_('Kaynak Veri'))
    anomaly_score = models.FloatField(_('Anomali Skoru'))
    description = models.TextField(_('Açıklama'))
    is_resolved = models.BooleanField(_('Çözüldü mü?'), default=False)
    resolution_notes = models.TextField(_('Çözüm Notları'), blank=True)
    detected_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Anomali Tespiti')
        verbose_name_plural = _('Anomali Tespitleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_detection_type_display()} - {self.created_at}"

class TrendAnalysis(models.Model):
    """Trend Analizi"""
    ANALYSIS_TYPES = [
        ('revenue', 'Gelir Trendi'),
        ('expense', 'Gider Trendi'),
        ('profit', 'Kâr Trendi'),
        ('cash_flow', 'Nakit Akış Trendi'),
    ]

    analysis_type = models.CharField(_('Analiz Tipi'), max_length=20, choices=ANALYSIS_TYPES)
    start_date = models.DateField(_('Başlangıç Tarihi'))
    end_date = models.DateField(_('Bitiş Tarihi'))
    trend_data = models.JSONField(_('Trend Verisi'))
    prediction = models.JSONField(_('Tahmin Verisi'))
    confidence_score = models.FloatField(_('Güven Skoru'))
    insights = models.TextField(_('İçgörüler'))
    analyzed_by = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Trend Analizi')
        verbose_name_plural = _('Trend Analizleri')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_analysis_type_display()} ({self.start_date} - {self.end_date})"

class UserPreference(models.Model):
    """Kullanıcı AI tercihleri"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='ai_preferences')
    language = models.CharField(_('Dil'), max_length=10, default='tr')
    risk_tolerance = models.CharField(_('Risk Toleransı'), max_length=20,
                                    choices=[('low', _('Düşük')),
                                            ('medium', _('Orta')),
                                            ('high', _('Yüksek'))])
    investment_horizon = models.CharField(_('Yatırım Vadesi'), max_length=20,
                                       choices=[('short', _('Kısa')),
                                               ('medium', _('Orta')),
                                               ('long', _('Uzun'))])
    notification_preferences = models.JSONField(_('Bildirim Tercihleri'), default=dict)
    ai_interaction_history = models.JSONField(_('AI Etkileşim Geçmişi'), default=list)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Güncellenme Tarihi'), auto_now=True)

    class Meta:
        verbose_name = _('Kullanıcı Tercihi')
        verbose_name_plural = _('Kullanıcı Tercihleri')

    def __str__(self):
        return f"{self.user.username} tercihleri"

class AIInsight(models.Model):
    """AI içgörüleri ve önerileri"""
    INSIGHT_TYPES = [
        ('investment', _('Yatırım Önerisi')),
        ('risk', _('Risk Uyarısı')),
        ('opportunity', _('Fırsat Bildirimi')),
        ('trend', _('Trend Analizi')),
    ]

    PRIORITY_LEVELS = [
        ('low', _('Düşük')),
        ('medium', _('Orta')),
        ('high', _('Yüksek')),
        ('urgent', _('Acil')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='ai_insights')
    insight_type = models.CharField(_('İçgörü Tipi'), max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(_('Başlık'), max_length=200)
    content = models.TextField(_('İçerik'))
    priority = models.CharField(_('Öncelik'), max_length=20, choices=PRIORITY_LEVELS)
    action_required = models.BooleanField(_('Aksiyon Gerekli'), default=False)
    action_description = models.TextField(_('Aksiyon Açıklaması'), blank=True)
    is_read = models.BooleanField(_('Okundu'), default=False)
    is_archived = models.BooleanField(_('Arşivlendi'), default=False)
    created_at = models.DateTimeField(_('Oluşturulma Tarihi'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Geçerlilik Sonu'), null=True, blank=True)

    class Meta:
        verbose_name = _('AI İçgörüsü')
        verbose_name_plural = _('AI İçgörüleri')
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Recommendation(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    recommendations = models.JSONField()
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    action_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']
