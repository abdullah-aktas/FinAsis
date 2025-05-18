# -*- coding: utf-8 -*-
import logging
from typing import Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
from django.contrib.auth.models import User
from ..models import FinancialReport, FinancialPrediction

logger = logging.getLogger(__name__)

class LegacyFinancialAIService:
    def __init__(self):
        """Finansal AI servisi başlatıcı"""
        pass
        
    def analyze_financial_data(self, user: User, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finansal verileri analiz eder
        
        Args:
            user (User): Kullanıcı nesnesi
            data (dict): Analiz edilecek finansal veriler
            
        Returns:
            dict: Analiz sonuçları
        """
        try:
            # Verileri DataFrame'e dönüştür
            df = pd.DataFrame(data)
            
            # Temel istatistikler
            stats = {
                'mean': df.mean().to_dict(),
                'median': df.median().to_dict(),
                'std': df.std().to_dict(),
                'min': df.min().to_dict(),
                'max': df.max().to_dict()
            }
            
            # Trend analizi
            trends = self._analyze_trends(df)
            
            # Anomali tespiti
            anomalies = self._detect_anomalies(df)
            
            # Tahminler
            predictions = self._generate_predictions(df)
            
            # Rapor oluştur
            report = FinancialReport.objects.create(
                user=user,
                title=f"Finansal Analiz Raporu - {datetime.now().strftime('%Y-%m-%d')}",
                report_type='analysis',
                content={
                    'statistics': stats,
                    'trends': trends,
                    'anomalies': anomalies,
                    'predictions': predictions
                },
                parameters=data
            )
            
            return {
                'report_id': report.id,  # type: ignore
                'statistics': stats,
                'trends': trends,
                'anomalies': anomalies,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Finansal veri analizi hatası: {str(e)}")
            raise
            
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Verilerdeki trendleri analiz eder
        
        Args:
            df (DataFrame): Analiz edilecek veriler
            
        Returns:
            dict: Trend analizi sonuçları
        """
        trends = {}
        
        # Her sütun için trend analizi
        for column in df.columns:
            if df[column].dtype in [np.float64, np.int64]:
                # Hareketli ortalama
                ma = df[column].rolling(window=3).mean()
                
                # Trend yönü
                slope = np.polyfit(range(len(df)), df[column], 1)[0]
                direction = 'artış' if slope > 0 else 'azalış' if slope < 0 else 'stabil'
                
                trends[column] = {
                    'moving_average': ma.tolist(),
                    'direction': direction,
                    'slope': slope
                }
                
        return trends
        
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Verilerdeki anormallikleri tespit eder
        
        Args:
            df (DataFrame): Analiz edilecek veriler
            
        Returns:
            dict: Anomali tespiti sonuçları
        """
        anomalies = {}
        
        # Her sütun için anomali tespiti
        for column in df.columns:
            if df[column].dtype in [np.float64, np.int64]:
                # Z-score hesapla
                z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                
                # Anormallikleri belirle (z-score > 3)
                anomaly_indices = np.where(z_scores > 3)[0]
                
                if len(anomaly_indices) > 0:
                    anomalies[column] = {
                        'indices': anomaly_indices.tolist(),
                        'values': df[column].iloc[anomaly_indices].tolist(),
                        'z_scores': z_scores[anomaly_indices].tolist()
                    }
                    
        return anomalies
        
    def _generate_predictions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Gelecekteki değerleri tahmin eder
        
        Args:
            df (DataFrame): Analiz edilecek veriler
            
        Returns:
            dict: Tahmin sonuçları
        """
        predictions = {}
        
        # Her sütun için tahmin
        for column in df.columns:
            if df[column].dtype in [np.float64, np.int64]:
                # Basit doğrusal regresyon
                x = np.array(range(len(df)))
                y = df[column].values
                
                # Model parametreleri
                if len(x) > 1 and len(y) > 1 and len(x) == len(y):
                    x = np.asarray(x, dtype=np.float64).reshape(-1)
                    y = np.asarray(y, dtype=np.float64).reshape(-1)
                    slope, intercept = np.polyfit(x, y, 1)
                else:
                    slope, intercept = 0, y[0] if len(y) > 0 else 0
                
                # Gelecek 5 dönem için tahmin
                future_x = np.array(range(len(df), len(df) + 5))
                future_y = slope * future_x + intercept
                
                predictions[column] = {
                    'future_values': future_y.tolist(),
                    'slope': slope,
                    'intercept': intercept
                }
                
        return predictions 