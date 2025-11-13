# -*- coding: utf-8 -*-
# type: ignore[reportAttributeAccessIssue]
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils import timezone
import json
from datetime import datetime, timedelta

# Optional scientific/ML stack (guard imports to keep startup lightweight in test/dev)
try:
    import pandas as pd
except Exception:  # pragma: no cover
    pd = None

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

try:
    from prophet import Prophet
except Exception:  # pragma: no cover
    Prophet = None

try:
    import plotly.graph_objects as go
except Exception:  # pragma: no cover
    go = None

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.model_selection import train_test_split
except Exception:  # pragma: no cover
    StandardScaler = LogisticRegression = DecisionTreeClassifier = train_test_split = None

try:
    import joblib
except Exception:  # pragma: no cover
    joblib = None

class AIModel(models.Model):
    """Yapay zeka modellerinin versiyonlarını ve performansını takip etmek için model"""
    MODEL_TYPES = [
        ('financial', _('Finansal Analiz')),
        ('recommendation', _('Öneri Sistemi')),
        ('chat', _('Sohbet Sistemi')),
        ('prediction', _('Tahmin Sistemi')),
    ]

    name = models.CharField(max_length=100, verbose_name=_('Model Adı'))
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES, verbose_name=_('Model Tipi'))
    version = models.CharField(max_length=20, verbose_name=_('Versiyon'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    accuracy = models.FloatField(_('Doğruluk Oranı'))
    parameters = models.JSONField(_('Model Parametreleri'), default=dict)
    last_trained = models.DateTimeField(_('Son Eğitim Tarihi'), auto_now=True)
    is_active = models.BooleanField(_('Aktif'), default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))

    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('AI Model')
        verbose_name_plural = _('AI Modeller')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"

class UserInteraction(models.Model):
    """Kullanıcı etkileşimlerini takip etmek için model"""
    INTERACTION_TYPES = [
        ('chat', _('Sohbet')),
        ('analysis', _('Analiz')),
        ('recommendation', _('Öneri')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Kullanıcı'))
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, verbose_name=_('Etkileşim Tipi'))
    content = models.TextField(verbose_name=_('İçerik'))  # Kullanıcının gönderdiği içerik
    ai_response = models.TextField(verbose_name=_('AI Yanıtı'))  # AI'ın verdiği yanıt
    feedback = models.IntegerField(_('Geri Bildirim'), null=True, blank=True)  # 1-5 arası puanlama
    feedback_text = models.TextField(_('Geri Bildirim Metni'), blank=True)
    processing_time = models.FloatField(_('İşlem Süresi'), help_text=_('Saniye cinsinden'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))

    class Meta:
        app_label = 'ai_assistant'
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Kullanıcı'))
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPES, verbose_name=_('Tahmin Tipi'))
    input_data = models.JSONField(verbose_name=_('Girdi Verileri'))
    prediction_result = models.TextField(verbose_name=_('Tahmin Sonucu'))  # AI'ın ürettiği tahmin sonucu
    confidence = models.FloatField(_('Güven Oranı'))
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, verbose_name=_('Kullanılan Model'), null=True, blank=True)
    is_validated = models.BooleanField(_('Doğrulandı'), default=False)
    validation_notes = models.TextField(_('Doğrulama Notları'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))

    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('Finansal Tahmin')
        verbose_name_plural = _('Finansal Tahminler')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.prediction_type} - {self.created_at}"

class AIFeedback(models.Model):
    """AI sisteminin performansını değerlendirmek için geri bildirim modeli"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Kullanıcı'))
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, verbose_name=_('Model'))
    rating = models.IntegerField(verbose_name=_('Değerlendirme'))
    feedback_text = models.TextField(blank=True, verbose_name=_('Geri Bildirim Metni'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))

    class Meta:
        app_label = 'ai_assistant'
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
        app_label = 'ai_assistant'
        verbose_name = _('Finansal Rapor')
        verbose_name_plural = _('Finansal Raporlar')
        ordering = ['-created_at']

    def __str__(self):
        try:
            report_type_display = self.get_report_type_display()
        except AttributeError:
            report_type_display = self.report_type
        return f"{self.title} - {report_type_display}"

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
        app_label = 'ai_assistant'
        verbose_name = _('Anomali Tespiti')
        verbose_name_plural = _('Anomali Tespitleri')
        ordering = ['-created_at']

    def __str__(self):
        try:
            detection_type_display = self.get_detection_type_display()
        except AttributeError:
            detection_type_display = self.detection_type
        return f"{detection_type_display} - {self.created_at}"

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
        app_label = 'ai_assistant'
        verbose_name = _('Trend Analizi')
        verbose_name_plural = _('Trend Analizleri')
        ordering = ['-created_at']

    def __str__(self):
        try:
            analysis_type_display = self.get_analysis_type_display()
        except AttributeError:
            analysis_type_display = self.analysis_type
        return f"{analysis_type_display} ({self.start_date} - {self.end_date})"

class UserPreference(models.Model):
    """Kullanıcı AI tercihleri"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Kullanıcı'))
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
    preferred_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, verbose_name=_('Tercih Edilen Model'))
    settings = models.JSONField(default=dict, verbose_name=_('Ayarlar'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))

    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('Kullanıcı Tercihi')
        verbose_name_plural = _('Kullanıcı Tercihleri')

    def __str__(self):
        return f"{self.user.username} - Tercihler"

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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Kullanıcı'))
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES, verbose_name=_('İçgörü Türü'))
    title = models.CharField(_('Başlık'), max_length=200)
    content = models.TextField(_('İçerik'))
    priority = models.CharField(_('Öncelik'), max_length=20, choices=PRIORITY_LEVELS)
    action_required = models.BooleanField(_('Aksiyon Gerekli'), default=False)
    action_description = models.TextField(_('Aksiyon Açıklaması'), blank=True)
    is_read = models.BooleanField(_('Okundu'), default=False)
    is_archived = models.BooleanField(_('Arşivlendi'), default=False)
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, verbose_name=_('Model'))
    insight_data = models.JSONField(verbose_name=_('İçgörü Verisi'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    expires_at = models.DateTimeField(_('Geçerlilik Sonu'), null=True, blank=True)

    class Meta:
        app_label = 'ai_assistant'
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    recommendations = models.JSONField()
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    action_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ai_assistant'

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        app_label = 'ai_assistant'
        ordering = ['-created_at']


class SectorBenchmark(models.Model):
    """Sektör bazlı finansal oran hedefleri (admin üzerinden yönetilir)."""
    sector_key = models.CharField(max_length=50, unique=True, verbose_name=_('Sektör Anahtarı (slug)'))
    display_name = models.CharField(max_length=100, verbose_name=_('Görünen Ad'))
    margin_min = models.FloatField(null=True, blank=True, verbose_name=_('Hedef Net Kar Marjı Min (%)'))
    current_ratio_min = models.FloatField(null=True, blank=True, verbose_name=_('Hedef Cari Oran Min'))
    dte_max = models.FloatField(null=True, blank=True, verbose_name=_('Hedef Borç/Özsermaye Max'))
    opex_ratio_max = models.FloatField(null=True, blank=True, verbose_name=_('Hedef Faaliyet Gider Oranı Max'))
    is_active = models.BooleanField(default=True, verbose_name=_('Aktif'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('Sektör Kıyas Hedefi')
        verbose_name_plural = _('Sektör Kıyas Hedefleri')
        ordering = ['sector_key']

    def __str__(self):
        return f"{self.display_name} ({self.sector_key})"

class CashFlowForecaster:
    def __init__(self, model_type='prophet'):
        """
        Nakit akışı tahminleme modeli
        
        Args:
            model_type (str): Kullanılacak model tipi ('prophet')
        """
        self.model_type = model_type
        self.model = None
        
    def prepare_data(self, data):
        """
        Veriyi model için hazırlar
        
        Args:
            data (pd.DataFrame): Tarih, gelir ve gider verilerini içeren DataFrame
        """
        if pd is None:
            raise ImportError("pandas kütüphanesi yüklü değil")
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['net_cash'] = df['cash_in'] - df['cash_out']
        return df
        
    def train(self, data):
        """
        Modeli eğitir
        
        Args:
            data (pd.DataFrame): Eğitim verisi
        """
        if Prophet is None:
            raise ImportError("prophet kütüphanesi yüklü değil veya devre dışı")
        df = self.prepare_data(data)
        prophet_df = df[['date', 'net_cash']].rename(columns={'date': 'ds', 'net_cash': 'y'})
        # Prophet parametreleri: 'auto', True veya False değerleri alabilir
        self.model = Prophet(yearly_seasonality='auto', weekly_seasonality='auto')  # type: ignore
        self.model.fit(prophet_df)
            
    def forecast(self, periods=90):
        """
        Gelecek dönemler için tahmin yapar
        
        Args:
            periods (int): Tahmin edilecek gün sayısı
            
        Returns:
            dict: Tahmin sonuçları
        """
        if self.model is None:
            raise ValueError("Model henüz eğitilmedi. Önce train() metodunu çağırın.")
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        
        # Sonuçları JSON formatına dönüştür
        results = {
            'dates': forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'predictions': forecast['yhat'].round(2).tolist(),
            'lower_bound': forecast['yhat_lower'].round(2).tolist(),
            'upper_bound': forecast['yhat_upper'].round(2).tolist()
        }
        return results
    
    def plot_forecast(self, results):
        """
        Tahmin sonuçlarını görselleştirir
        
        Args:
            results (dict): Tahmin sonuçları
            
        Returns:
            plotly.graph_objects.Figure: Grafik
        """
        if go is None:
            raise ImportError("plotly kütüphanesi yüklü değil")
        fig = go.Figure()
        
        # Tahmin çizgisi
        fig.add_trace(go.Scatter(
            x=results['dates'],
            y=results['predictions'],
            name='Tahmin',
            line=dict(color='blue')
        ))
        
        # Güven aralığı
        fig.add_trace(go.Scatter(
            x=results['dates'] + results['dates'][::-1],
            y=results['upper_bound'] + results['lower_bound'][::-1],
            fill='toself',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Güven Aralığı'
        ))
        
        fig.update_layout(
            title='Nakit Akışı Tahmini',
            xaxis_title='Tarih',
            yaxis_title='Net Nakit Akışı',
            template='plotly_white'
        )
        
        return fig

class CustomerRiskScorer:
    def __init__(self, model_type='logistic'):
        """
        Müşteri risk skorlama modeli
        
        Args:
            model_type (str): Kullanılacak model tipi ('logistic', 'tree')
        """
        self.model_type = model_type
        self.model = None
        if StandardScaler is None:
            raise ImportError("sklearn kütüphanesi yüklü değil")
        self.scaler = StandardScaler()
        
    def prepare_features(self, data):
        """
        Özellikleri hazırlar
        
        Args:
            data (dict): Müşteri verileri
        """
        if pd is None:
            raise ImportError("pandas kütüphanesi yüklü değil")
        features = {
            'payment_delay_avg': data.get('payment_delay_avg', 0),
            'payment_delay_count': data.get('payment_delay_count', 0),
            'transaction_amount_avg': data.get('transaction_amount_avg', 0),
            'transaction_count': data.get('transaction_count', 0),
            'days_since_last_payment': data.get('days_since_last_payment', 0),
            'sector_risk_score': data.get('sector_risk_score', 0)
        }
        return pd.DataFrame([features])
        
    def train(self, training_data):
        """
        Modeli eğitir
        
        Args:
            training_data (pd.DataFrame): Eğitim verisi
        """
        if LogisticRegression is None or DecisionTreeClassifier is None:
            raise ImportError("sklearn kütüphanesi yüklü değil")
            
        X = training_data.drop('risk_label', axis=1)
        y = training_data['risk_label']
        
        # Veriyi ölçeklendir
        X_scaled = self.scaler.fit_transform(X)
        
        # Model seçimi ve eğitimi
        if self.model_type == 'logistic':
            self.model = LogisticRegression(max_iter=1000)
        else:
            self.model = DecisionTreeClassifier(max_depth=5)
            
        self.model.fit(X_scaled, y)
        
    def predict_risk_score(self, customer_data):
        """
        Müşteri için risk skoru tahmin eder
        
        Args:
            customer_data (dict): Müşteri verileri
            
        Returns:
            dict: Risk skoru ve açıklaması
        """
        if self.model is None:
            raise ValueError("Model henüz eğitilmedi. Önce train() metodunu çağırın.")
            
        features = self.prepare_features(customer_data)
        features_scaled = self.scaler.transform(features)
        
        # Risk olasılığını tahmin et
        risk_prob = self.model.predict_proba(features_scaled)[0][1]
        
        # 0-100 arası skora dönüştür
        risk_score = int(risk_prob * 100)
        
        # Risk seviyesini belirle
        if risk_score >= 80:
            risk_level = 'Yüksek'
            color = 'red'
        elif risk_score >= 60:
            risk_level = 'Orta'
            color = 'orange'
        else:
            risk_level = 'Düşük'
            color = 'green'
            
        # Risk açıklaması oluştur
        explanation = self._generate_explanation(customer_data, risk_score)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'color': color,
            'explanation': explanation
        }
        
    def _generate_explanation(self, customer_data, risk_score):
        """
        Risk skoru için açıklama oluşturur
        
        Args:
            customer_data (dict): Müşteri verileri
            risk_score (int): Risk skoru
            
        Returns:
            str: Risk açıklaması
        """
        explanations = []
        
        if customer_data.get('payment_delay_count', 0) > 0:
            explanations.append(f"Son dönemde {customer_data['payment_delay_count']} kez ödeme gecikmesi yaşandı")
            
        if customer_data.get('payment_delay_avg', 0) > 15:
            explanations.append(f"Ortalama ödeme gecikmesi {customer_data['payment_delay_avg']:.1f} gün")
            
        if customer_data.get('transaction_amount_avg', 0) < 1000:
            explanations.append("İşlem hacmi düşük")
            
        if customer_data.get('days_since_last_payment', 0) > 30:
            explanations.append(f"Son ödemeden bu yana {customer_data['days_since_last_payment']} gün geçti")
            
        if not explanations:
            explanations.append("Risk faktörü tespit edilmedi")
            
        return ". ".join(explanations)
        
    def save_model(self, path):
        """
        Modeli kaydeder
        
        Args:
            path (str): Kayıt yolu
        """
        if joblib is None:
            raise ImportError("joblib kütüphanesi yüklü değil")
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type
        }
        joblib.dump(model_data, path)
        
    def load_model(self, path):
        """
        Modeli yükler
        
        Args:
            path (str): Model dosyası yolu
        """
        if joblib is None:
            raise ImportError("joblib kütüphanesi yüklü değil")
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']

class MarketAnalysis(models.Model):
    """Piyasa analizi modeli"""
    asset = models.CharField(max_length=50)
    current_price = models.FloatField()
    change_percent = models.FloatField()
    trend = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ai_assistant'
        verbose_name = 'Piyasa Analizi'
        verbose_name_plural = 'Piyasa Analizleri'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.asset} - {self.timestamp}"


class SentimentAnalysis(models.Model):
    """Sentiment (duygu) analizi sonuçları"""
    SENTIMENT_CHOICES = [
        ('positive', _('Pozitif')),
        ('neutral', _('Nötr')),
        ('negative', _('Negatif')),
    ]
    
    SOURCE_TYPES = [
        ('customer_feedback', _('Müşteri Geri Bildirimi')),
        ('invoice_note', _('Fatura Notu')),
        ('email', _('E-posta')),
        ('chat', _('Sohbet')),
        ('review', _('Değerlendirme')),
        ('social_media', _('Sosyal Medya')),
        ('document', _('Doküman')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sentiment_analyses')
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPES, verbose_name=_('Kaynak Tipi'))
    text_content = models.TextField(verbose_name=_('Analiz Edilen Metin'))
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, verbose_name=_('Duygu'))
    confidence_score = models.FloatField(verbose_name=_('Güven Skoru'), help_text=_('0.0 - 1.0 arası'))
    positive_score = models.FloatField(default=0.0)
    neutral_score = models.FloatField(default=0.0)
    negative_score = models.FloatField(default=0.0)
    keywords = models.JSONField(default=list, blank=True, verbose_name=_('Anahtar Kelimeler'))
    entities = models.JSONField(default=list, blank=True, verbose_name=_('Varlıklar'))
    language = models.CharField(max_length=5, default='tr', verbose_name=_('Dil'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    # İlişkili kayıt
    reference_model = models.CharField(max_length=50, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('Sentiment Analizi')
        verbose_name_plural = _('Sentiment Analizleri')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sentiment', 'source_type']),
        ]
    
    def __str__(self):
        return f"{self.get_sentiment_display()} - {self.source_type} ({self.confidence_score:.2f})"


class DocumentSummary(models.Model):
    """Doküman özetleme sonuçları"""
    DOCUMENT_TYPES = [
        ('invoice', _('Fatura')),
        ('contract', _('Sözleşme')),
        ('report', _('Rapor')),
        ('email', _('E-posta')),
        ('meeting_notes', _('Toplantı Notları')),
        ('financial_statement', _('Mali Tablo')),
        ('legal_doc', _('Hukuki Doküman')),
        ('other', _('Diğer')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_summaries')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES, verbose_name=_('Doküman Tipi'))
    original_text = models.TextField(verbose_name=_('Orijinal Metin'))
    summary = models.TextField(verbose_name=_('Özet'))
    summary_length = models.IntegerField(verbose_name=_('Özet Uzunluğu (kelime)'))
    original_length = models.IntegerField(verbose_name=_('Orijinal Uzunluk (kelime)'))
    compression_ratio = models.FloatField(verbose_name=_('Sıkıştırma Oranı'))
    key_points = models.JSONField(default=list, blank=True, verbose_name=_('Ana Noktalar'))
    entities_mentioned = models.JSONField(default=list, blank=True, verbose_name=_('Bahsedilen Varlıklar'))
    language = models.CharField(max_length=5, default='tr')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Dosya referansı (opsiyonel)
    document_file = models.FileField(upload_to='ai_summaries/', null=True, blank=True)
    
    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('Doküman Özeti')
        verbose_name_plural = _('Doküman Özetleri')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.created_at.strftime('%d.%m.%Y')}"


class AutoGeneratedReport(models.Model):
    """Otomatik üretilen raporlar"""
    REPORT_TYPES = [
        ('daily_summary', _('Günlük Özet')),
        ('weekly_performance', _('Haftalık Performans')),
        ('monthly_financial', _('Aylık Mali Rapor')),
        ('quarterly_review', _('Çeyreklik İnceleme')),
        ('annual_report', _('Yıllık Rapor')),
        ('cash_flow', _('Nakit Akışı')),
        ('profit_loss', _('Kar-Zarar')),
        ('expense_analysis', _('Gider Analizi')),
        ('customer_insights', _('Müşteri İçgörüleri')),
        ('custom', _('Özel Rapor')),
    ]
    
    STATUS_CHOICES = [
        ('generating', _('Oluşturuluyor')),
        ('completed', _('Tamamlandı')),
        ('failed', _('Başarısız')),
        ('scheduled', _('Planlandı')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auto_reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES, verbose_name=_('Rapor Tipi'))
    title = models.CharField(max_length=200, verbose_name=_('Rapor Başlığı'))
    content = models.TextField(verbose_name=_('Rapor İçeriği'), blank=True)
    summary = models.TextField(verbose_name=_('Özet'), blank=True)
    insights = models.JSONField(default=list, blank=True, verbose_name=_('İçgörüler'))
    metrics = models.JSONField(default=dict, blank=True, verbose_name=_('Metrikler'))
    charts_data = models.JSONField(default=dict, blank=True, verbose_name=_('Grafik Verileri'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    
    # Tarih aralığı
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    
    # Dosya export
    pdf_file = models.FileField(upload_to='ai_reports/pdf/', null=True, blank=True)
    excel_file = models.FileField(upload_to='ai_reports/excel/', null=True, blank=True)
    
    # Zamanlanmış rapor
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)  # daily, weekly, monthly
    next_generation = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('Otomatik Rapor')
        verbose_name_plural = _('Otomatik Raporlar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'report_type']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class AdvancedAnalytics(models.Model):
    """Gelişmiş analitik sonuçları"""
    ANALYTICS_TYPES = [
        ('revenue_forecast', _('Gelir Tahmini')),
        ('expense_pattern', _('Gider Deseni')),
        ('customer_segmentation', _('Müşteri Segmentasyonu')),
        ('churn_prediction', _('Müşteri Kaybı Tahmini')),
        ('profitability_analysis', _('Karlılık Analizi')),
        ('market_basket', _('Market Basket Analizi')),
        ('cohort_analysis', _('Kohort Analizi')),
        ('abc_analysis', _('ABC Analizi')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='advanced_analytics')
    analytics_type = models.CharField(max_length=30, choices=ANALYTICS_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Analiz sonuçları
    results = models.JSONField(default=dict, verbose_name=_('Analiz Sonuçları'))
    visualizations = models.JSONField(default=dict, verbose_name=_('Görselleştirmeler'))
    recommendations = models.JSONField(default=list, verbose_name=_('Öneriler'))
    
    # Metrikler
    accuracy_score = models.FloatField(null=True, blank=True)
    confidence_level = models.FloatField(null=True, blank=True)
    
    # Tarih bilgisi
    analysis_period_start = models.DateField(null=True, blank=True)
    analysis_period_end = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'ai_assistant'
        verbose_name = _('Gelişmiş Analitik')
        verbose_name_plural = _('Gelişmiş Analitikler')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_analytics_type_display()} - {self.title}"