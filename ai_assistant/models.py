from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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
