# -*- coding: utf-8 -*-
"""
Makine Öğrenmesi Servisleri
- Risk Skorlama (Logistic Regression)
- Finansal Tahmin (Prophet)
- Öneri Sistemi (kural tabanlı/ML)
"""
from typing import Any, Dict, Optional
import numpy as np
import joblib
import os
from sklearn.linear_model import LogisticRegression
from prophet import Prophet
import pandas as pd
import datetime
from django.utils import timezone
from ..models import AIModel, UserInteraction
from django.contrib.auth import get_user_model

User = get_user_model()

class RiskScoringService:
    """
    Müşteri risk skoru için Logistic Regression tabanlı servis
    """
    log_file = 'risk_model.log'

    def __init__(self, model_path: str = 'risk_model.pkl'):
        self.model_path = model_path
        self.model: Optional[LogisticRegression] = self.load_model()

    def train(self, X: np.ndarray, y: np.ndarray, user=None) -> None:
        """Modeli eğitir ve kaydeder."""
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)
        self.save_model()
        accuracy = self.model.score(X, y)
        params = self.model.get_params()
        # AIModel güncelle
        model_obj, created = AIModel.objects.update_or_create(
            name='RiskScoringModel',
            model_type='risk',
            defaults={
                'version': timezone.now().strftime('%Y%m%d%H%M%S'),
                'accuracy': accuracy,
                'parameters': params,
                'last_trained': timezone.now(),
                'is_active': True,
                'description': 'Logistic Regression tabanlı risk skorlama modeli.'
            }
        )
        self.log_event('Model yeniden eğitildi. Doğruluk: %.4f' % accuracy, user)

    def save_model(self) -> None:
        if self.model:
            joblib.dump(self.model, self.model_path)
            self.log_event('Model kaydedildi.')

    def load_model(self) -> Optional[LogisticRegression]:
        if os.path.exists(self.model_path):
            self.log_event('Model yüklendi.')
            return joblib.load(self.model_path)
        return None

    def predict(self, features: np.ndarray, user=None) -> dict:
        if self.model is None:
            raise Exception("Model eğitilmemiş!")
        score = float(self.model.predict_proba(features.reshape(1, -1))[0, 1])
        # AIModel'den versiyon ve parametre çek
        try:
            model_obj = AIModel.objects.get(name='RiskScoringModel', model_type='risk')
            version = model_obj.version
            params = model_obj.parameters
        except AIModel.DoesNotExist:
            version = None
            params = None
        # Feature importances (Logistic Regression coef)
        feature_names = [
            'Ortalama Gecikme', 'Gecikme Sayısı', 'Ortalama İşlem Tutarı',
            'İşlem Sayısı', 'Son Ödemeden Geçen Gün', 'Sektör Risk Skoru'
        ]
        importances = np.abs(self.model.coef_[0])
        total = importances.sum() if importances.sum() > 0 else 1
        norm_importances = importances / total
        explanation = {
            'features': [
                {'name': n, 'value': float(v), 'importance': float(i)}
                for n, v, i in zip(feature_names, features, norm_importances)
            ],
            'summary': f"En çok etki eden faktör: {feature_names[int(np.argmax(norm_importances))]}"
        }
        self.log_event(f'Tahmin yapıldı. Skor: {score:.4f}', user)
        return {
            'risk_score': score,
            'model_version': version,
            'model_parameters': params,
            'explanation': explanation
        }

    def log_event(self, message: str, user=None) -> None:
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
        if user:
            UserInteraction.objects.create(
                user=user,
                interaction_type='analysis',
                content=message,
                ai_response='',
                processing_time=0.0
            )

class FinancialForecastService:
    """
    Prophet tabanlı finansal tahmin servisi
    """
    log_file = 'forecast_model.log'

    def __init__(self):
        self.model: Optional[Prophet] = None

    def train(self, df: pd.DataFrame, user=None) -> None:
        """Prophet ile modeli eğitir. df: ['ds', 'y'] sütunları olmalı."""
        self.model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
        self.model.fit(df)
        # AIModel güncelle
        params = {'yearly_seasonality': True, 'weekly_seasonality': True}
        model_obj, created = AIModel.objects.update_or_create(
            name='FinancialForecastModel',
            model_type='financial',
            defaults={
                'version': timezone.now().strftime('%Y%m%d%H%M%S'),
                'accuracy': 0.0,  # Prophet için cross-val eklenebilir
                'parameters': params,
                'last_trained': timezone.now(),
                'is_active': True,
                'description': 'Prophet tabanlı finansal tahmin modeli.'
            }
        )
        self.log_event('Prophet modeli yeniden eğitildi.', user)

    def forecast(self, periods: int = 90, user=None) -> dict:
        if self.model is None:
            raise Exception("Model eğitilmemiş!")
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        try:
            model_obj = AIModel.objects.get(name='FinancialForecastModel', model_type='financial')
            version = model_obj.version
            params = model_obj.parameters
        except AIModel.DoesNotExist:
            version = None
            params = None
        self.log_event(f'{periods} gün için tahmin üretildi.', user)
        # Prophet explainability (örnek): trend, seasonality, en yüksek tahmin günü
        max_idx = forecast['yhat'].idxmax()
        explanation = {
            'features': [
                {'name': 'Trend', 'value': float(forecast['trend'].iloc[-1]), 'importance': 0.4},
                {'name': 'Yearly Seasonality', 'value': float(forecast['yearly'].iloc[-1]) if 'yearly' in forecast else 0, 'importance': 0.3},
                {'name': 'Weekly Seasonality', 'value': float(forecast['weekly'].iloc[-1]) if 'weekly' in forecast else 0, 'importance': 0.2},
                {'name': 'En Yüksek Tahmin Günü', 'value': str(forecast['ds'].iloc[max_idx]), 'importance': 0.1}
            ],
            'summary': f"Tahmin edilen en yüksek değer: {forecast['yhat'].iloc[max_idx]:.2f} ({forecast['ds'].iloc[max_idx]})"
        }
        return {
            'dates': forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'predictions': forecast['yhat'].round(2).tolist(),
            'lower_bound': forecast['yhat_lower'].round(2).tolist(),
            'upper_bound': forecast['yhat_upper'].round(2).tolist(),
            'model_version': version,
            'model_parameters': params,
            'explanation': explanation
        }

    def log_event(self, message: str, user=None) -> None:
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
        if user:
            UserInteraction.objects.create(
                user=user,
                interaction_type='analysis',
                content=message,
                ai_response='',
                processing_time=0.0
            )

class RecommendationService:
    """
    Basit kural tabanlı veya ML tabanlı öneri sistemi
    """
    def generate(self, data: Dict[str, Any]) -> dict:
        """Kullanıcı finansal verilerine göre öneri ve model meta verisi üretir."""
        income = data.get('income', 0)
        expenses = data.get('expenses', 0)
        savings = data.get('savings', 0)
        goal = data.get('goals', '')
        if income - expenses > 0 and savings > 0:
            if goal == 'investment':
                rec = "Birikiminizin bir kısmını düşük riskli yatırım araçlarında değerlendirebilirsiniz."
            elif goal == 'savings':
                rec = "Düzenli olarak birikim yapmaya devam edin."
            elif goal == 'debt':
                rec = "Öncelikle borçlarınızı kapatmaya odaklanın."
            elif goal == 'retirement':
                rec = "Emeklilik için uzun vadeli yatırım fonlarını inceleyin."
            else:
                rec = "Finansal durumunuz iyi, hedeflerinize uygun plan yapabilirsiniz."
        else:
            rec = "Giderlerinizi azaltmayı ve acil durum fonu oluşturmayı düşünün."
        # Model meta verisi örnek
        return {
            'recommendation': rec,
            'model_version': 'v1.0.0',
            'model_parameters': {'type': 'rule-based', 'rules': 5}
        } 