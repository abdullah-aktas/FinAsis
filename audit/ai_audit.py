"""
AI-Powered Audit Analysis Module
Yapay Zeka Destekli Denetim ve Analiz Sistemi
"""
import numpy as np
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from typing import Dict, List, Any, Tuple
import json


class AuditAIAnalyzer:
    """
    Yapay Zeka Destekli Audit Analizi
    - Anomali tespiti
    - Risk skorlama
    - Tahminsel analizler
    - Otomatik öneriler
    """
    
    # Risk ağırlıkları
    RISK_WEIGHTS = {
        'frequency': 0.25,      # İşlem sıklığı
        'severity': 0.30,       # Ciddiyet seviyesi
        'financial': 0.25,      # Finansal etki
        'time_pattern': 0.20,   # Zaman deseni
    }
    
    # Anomali eşik değerleri
    ANOMALY_THRESHOLDS = {
        'frequency_stddev': 3.0,    # 3 standart sapma
        'amount_stddev': 2.5,       # 2.5 standart sapma
        'time_anomaly': 0.8,        # 80% sapma
    }
    
    @classmethod
    def detect_anomalies(cls, audit_events, lookback_days=30) -> List[Dict[str, Any]]:
        """
        Anomali Tespiti - İstatistiksel ve makine öğrenmesi tabanlı
        
        Args:
            audit_events: QuerySet of AuditEvent
            lookback_days: Kaç günlük geçmiş analiz edilecek
            
        Returns:
            List of detected anomalies with details
        """
        anomalies = []
        
        # Tarih aralığı
        cutoff_date = timezone.now() - timedelta(days=lookback_days)
        recent_events = audit_events.filter(created_at__gte=cutoff_date)
        
        # 1. Sıklık Anomalisi - Olağandışı yüksek işlem sayısı
        frequency_anomalies = cls._detect_frequency_anomalies(recent_events)
        anomalies.extend(frequency_anomalies)
        
        # 2. Tutar Anomalisi - Olağandışı yüksek/düşük tutarlar
        amount_anomalies = cls._detect_amount_anomalies(recent_events)
        anomalies.extend(amount_anomalies)
        
        # 3. Zaman Anomalisi - Olağandışı saatlerde işlem
        time_anomalies = cls._detect_time_anomalies(recent_events)
        anomalies.extend(time_anomalies)
        
        # 4. Desen Anomalisi - Olağandışı davranış desenleri
        pattern_anomalies = cls._detect_pattern_anomalies(recent_events)
        anomalies.extend(pattern_anomalies)
        
        # 5. Coğrafi Anomali - Farklı lokasyonlardan erişim
        geo_anomalies = cls._detect_geographic_anomalies(recent_events)
        anomalies.extend(geo_anomalies)
        
        return sorted(anomalies, key=lambda x: x['risk_score'], reverse=True)
    
    @classmethod
    def _detect_frequency_anomalies(cls, events) -> List[Dict]:
        """İşlem sıklığı anomalilerini tespit et"""
        anomalies = []
        
        # Kullanıcı bazında işlem sayıları
        user_activity = events.values('actor_username').annotate(
            count=Count('id')
        ).order_by('-count')
        
        if not user_activity:
            return anomalies
        
        # İstatistiksel analiz
        counts = [item['count'] for item in user_activity]
        mean = np.mean(counts)
        std = np.std(counts)
        threshold = mean + (cls.ANOMALY_THRESHOLDS['frequency_stddev'] * std)
        
        for item in user_activity:
            if item['count'] > threshold:
                anomalies.append({
                    'type': 'frequency',
                    'severity': 'high' if item['count'] > mean + 4*std else 'medium',
                    'user': item['actor_username'],
                    'description': f"Olağandışı yüksek işlem sayısı: {item['count']} (Normal: {mean:.0f}±{std:.0f})",
                    'risk_score': min(100, int((item['count'] / threshold) * 70)),
                    'details': {
                        'transaction_count': item['count'],
                        'average': mean,
                        'std_dev': std,
                        'threshold': threshold
                    }
                })
        
        return anomalies
    
    @classmethod
    def _detect_amount_anomalies(cls, events) -> List[Dict]:
        """Finansal tutar anomalilerini tespit et"""
        anomalies = []
        
        # Finansal etkisi olan olaylar
        financial_events = events.filter(financial_impact__isnull=False)
        
        if not financial_events.exists():
            return anomalies
        
        amounts = list(financial_events.values_list('financial_impact', flat=True))
        mean = np.mean(amounts)
        std = np.std(amounts)
        threshold_high = mean + (cls.ANOMALY_THRESHOLDS['amount_stddev'] * std)
        
        for event in financial_events.filter(financial_impact__gt=threshold_high):
            anomalies.append({
                'type': 'amount',
                'severity': 'high' if event.financial_impact > mean + 4*std else 'medium',
                'user': event.actor_username,
                'description': f"Olağandışı yüksek tutar: {event.financial_impact:,.2f} TL (Normal: {mean:,.0f}±{std:,.0f})",
                'risk_score': min(100, int((float(event.financial_impact) / float(threshold_high)) * 80)),
                'details': {
                    'amount': float(event.financial_impact),
                    'average': mean,
                    'std_dev': std,
                    'event_id': event.id,
                    'action': event.action
                }
            })
        
        return anomalies
    
    @classmethod
    def _detect_time_anomalies(cls, events) -> List[Dict]:
        """Zaman deseni anomalilerini tespit et (mesai dışı işlemler)"""
        anomalies = []
        
        # Mesai saatleri dışı işlemler (22:00 - 06:00)
        off_hours_events = events.extra(
            where=["EXTRACT(HOUR FROM created_at) >= 22 OR EXTRACT(HOUR FROM created_at) <= 6"]
        ).filter(severity__in=['medium', 'high', 'critical'])
        
        for event in off_hours_events:
            hour = event.created_at.hour
            anomalies.append({
                'type': 'time',
                'severity': 'medium',
                'user': event.actor_username,
                'description': f"Mesai saatleri dışı kritik işlem: {event.get_action_display()} (Saat: {hour:02d}:00)",
                'risk_score': 60,
                'details': {
                    'hour': hour,
                    'action': event.action,
                    'event_id': event.id,
                    'timestamp': event.created_at.isoformat()
                }
            })
        
        return anomalies
    
    @classmethod
    def _detect_pattern_anomalies(cls, events) -> List[Dict]:
        """Davranış deseni anomalilerini tespit et"""
        anomalies = []
        
        # Ardışık başarısız giriş denemeleri
        failed_logins = events.filter(
            action='login',
            severity__in=['high', 'critical']
        ).order_by('actor_username', 'created_at')
        
        user_attempts = {}
        for event in failed_logins:
            user = event.actor_username
            if user not in user_attempts:
                user_attempts[user] = []
            user_attempts[user].append(event)
        
        for user, attempts in user_attempts.items():
            if len(attempts) >= 5:  # 5+ başarısız deneme
                anomalies.append({
                    'type': 'pattern',
                    'severity': 'high',
                    'user': user,
                    'description': f"Şüpheli giriş denemeleri: {len(attempts)} başarısız deneme",
                    'risk_score': min(100, len(attempts) * 15),
                    'details': {
                        'attempt_count': len(attempts),
                        'first_attempt': attempts[0].created_at.isoformat(),
                        'last_attempt': attempts[-1].created_at.isoformat()
                    }
                })
        
        return anomalies
    
    @classmethod
    def _detect_geographic_anomalies(cls, events) -> List[Dict]:
        """Coğrafi konum anomalilerini tespit et"""
        anomalies = []
        
        # Kullanıcı başına farklı IP adreslerinden erişim
        user_ips = events.filter(ip__isnull=False).values(
            'actor_username'
        ).annotate(
            unique_ips=Count('ip', distinct=True)
        ).filter(unique_ips__gte=5)  # 5+ farklı IP
        
        for item in user_ips:
            anomalies.append({
                'type': 'geographic',
                'severity': 'medium',
                'user': item['actor_username'],
                'description': f"Çoklu lokasyondan erişim: {item['unique_ips']} farklı IP adresi",
                'risk_score': min(100, item['unique_ips'] * 10),
                'details': {
                    'unique_ip_count': item['unique_ips']
                }
            })
        
        return anomalies
    
    @classmethod
    def calculate_risk_score(cls, entity_data: Dict) -> Tuple[int, Dict]:
        """
        Kapsamlı risk skoru hesaplama
        
        Returns:
            (risk_score, risk_breakdown)
        """
        scores = {}
        
        # 1. Sıklık Riski
        frequency_score = cls._calculate_frequency_risk(entity_data.get('transaction_count', 0))
        scores['frequency'] = frequency_score
        
        # 2. Ciddiyet Riski
        severity_score = cls._calculate_severity_risk(entity_data.get('high_severity_count', 0))
        scores['severity'] = severity_score
        
        # 3. Finansal Risk
        financial_score = cls._calculate_financial_risk(entity_data.get('total_financial_impact', 0))
        scores['financial'] = financial_score
        
        # 4. Zaman Deseni Riski
        time_score = cls._calculate_time_risk(entity_data.get('off_hours_count', 0))
        scores['time_pattern'] = time_score
        
        # Ağırlıklı toplam
        total_risk = sum(scores[key] * cls.RISK_WEIGHTS[key] for key in scores)
        
        return int(total_risk), scores
    
    @classmethod
    def _calculate_frequency_risk(cls, count: int) -> int:
        """İşlem sıklığı riski (0-100)"""
        if count < 10:
            return 10
        elif count < 50:
            return 30
        elif count < 100:
            return 50
        elif count < 500:
            return 70
        else:
            return 90
    
    @classmethod
    def _calculate_severity_risk(cls, high_count: int) -> int:
        """Ciddiyet riski (0-100)"""
        if high_count == 0:
            return 5
        elif high_count < 3:
            return 40
        elif high_count < 10:
            return 70
        else:
            return 95
    
    @classmethod
    def _calculate_financial_risk(cls, total_impact: float) -> int:
        """Finansal risk (0-100)"""
        if total_impact < 1000:
            return 10
        elif total_impact < 10000:
            return 30
        elif total_impact < 50000:
            return 50
        elif total_impact < 100000:
            return 70
        else:
            return 90
    
    @classmethod
    def _calculate_time_risk(cls, off_hours: int) -> int:
        """Zaman deseni riski (0-100)"""
        if off_hours == 0:
            return 5
        elif off_hours < 5:
            return 30
        elif off_hours < 15:
            return 60
        else:
            return 85
    
    @classmethod
    def generate_recommendations(cls, anomalies: List[Dict], risk_score: int) -> List[Dict]:
        """
        Akıllı öneriler oluştur
        
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Risk seviyesine göre genel öneriler
        if risk_score > 80:
            recommendations.append({
                'priority': 'critical',
                'category': 'security',
                'title': 'Acil Güvenlik İncelemesi Gerekli',
                'description': 'Yüksek risk seviyesi tespit edildi. Derhal güvenlik uzmanı ile görüşün.',
                'actions': [
                    'Tüm kullanıcı hesaplarını gözden geçirin',
                    'Şifre değişikliği zorunlu kılın',
                    'İki faktörlü kimlik doğrulamayı etkinleştirin',
                    'Erişim loglarını detaylı inceleyin'
                ]
            })
        
        # Anomali tipine göre özel öneriler
        anomaly_types = [a['type'] for a in anomalies]
        
        if 'frequency' in anomaly_types:
            recommendations.append({
                'priority': 'high',
                'category': 'operational',
                'title': 'İşlem Sıklığı Kontrolü',
                'description': 'Olağandışı yüksek işlem sayısı tespit edildi.',
                'actions': [
                    'Otomatik işlem limitleri belirleyin',
                    'Kullanıcı aktivite raporlarını inceleyin',
                    'Bot/script kullanımı kontrolü yapın'
                ]
            })
        
        if 'amount' in anomaly_types:
            recommendations.append({
                'priority': 'critical',
                'category': 'financial',
                'title': 'Finansal İşlem Kontrolü',
                'description': 'Olağandışı yüksek tutarda işlemler tespit edildi.',
                'actions': [
                    'Finansal işlemlerde onay mekanizması ekleyin',
                    'Tutar limitlerini gözden geçirin',
                    'Çift imza zorunluluğu getirin',
                    'Otomatik ödeme sistemlerini kontrol edin'
                ]
            })
        
        if 'time' in anomaly_types:
            recommendations.append({
                'priority': 'medium',
                'category': 'security',
                'title': 'Zaman Tabanlı Erişim Kontrolü',
                'description': 'Mesai saatleri dışı kritik işlemler tespit edildi.',
                'actions': [
                    'Mesai saatleri dışı erişim kısıtlaması getirin',
                    'Kritik işlemler için zaman penceresi tanımlayın',
                    'Acil durum prosedürlerini oluşturun'
                ]
            })
        
        if 'geographic' in anomaly_types:
            recommendations.append({
                'priority': 'high',
                'category': 'security',
                'title': 'Coğrafi Erişim Kontrolü',
                'description': 'Çoklu lokasyondan erişim tespit edildi.',
                'actions': [
                    'IP whitelisting uygulayın',
                    'VPN zorunluluğu getirin',
                    'Coğrafi konum tabanlı uyarılar aktifleştirin',
                    'Şüpheli lokasyonları engelleyin'
                ]
            })
        
        # KOBİ'ye özel öneriler
        recommendations.append({
            'priority': 'medium',
            'category': 'compliance',
            'title': 'Uyumluluk ve Raporlama',
            'description': 'Düzenli denetim raporları oluşturun.',
            'actions': [
                'Aylık audit raporlarını otomatikleştirin',
                'Yönetim kuruluna düzenli sunumlar yapın',
                'Mevzuat uyumluluğunu kontrol edin',
                'Dış denetim için hazırlık yapın'
            ]
        })
        
        return sorted(recommendations, key=lambda x: {'critical': 3, 'high': 2, 'medium': 1, 'low': 0}[x['priority']], reverse=True)
    
    @classmethod
    def predict_risk_trend(cls, historical_scores: List[Tuple[datetime, int]]) -> Dict:
        """
        Gelecekteki risk trendini tahmin et (basit regresyon)
        
        Args:
            historical_scores: [(date, risk_score), ...]
            
        Returns:
            Trend analysis and prediction
        """
        if len(historical_scores) < 2:
            return {'trend': 'insufficient_data', 'prediction': None}
        
        # Basit doğrusal regresyon
        x = np.array(range(len(historical_scores)))
        y = np.array([score for _, score in historical_scores])
        
        # Trend hesaplama
        slope = np.polyfit(x, y, 1)[0]
        
        # 30 gün sonrası tahmini
        next_30_days = len(historical_scores) + 30
        predicted_score = int(np.poly1d(np.polyfit(x, y, 1))(next_30_days))
        
        if slope > 5:
            trend = 'increasing'
            alert_level = 'warning'
        elif slope < -5:
            trend = 'decreasing'
            alert_level = 'good'
        else:
            trend = 'stable'
            alert_level = 'normal'
        
        return {
            'trend': trend,
            'slope': float(slope),
            'current_score': int(y[-1]),
            'predicted_score_30d': max(0, min(100, predicted_score)),
            'alert_level': alert_level,
            'recommendation': cls._get_trend_recommendation(trend, predicted_score)
        }
    
    @classmethod
    def _get_trend_recommendation(cls, trend: str, predicted_score: int) -> str:
        """Trend bazlı öneri"""
        if trend == 'increasing' and predicted_score > 70:
            return "Risk seviyesi artış trendinde! Önleyici aksiyonlar alın."
        elif trend == 'decreasing':
            return "Risk seviyesi azalış trendinde. Mevcut kontrolleri sürdürün."
        elif predicted_score > 80:
            return "Yüksek risk tahmini! Acil aksiyon planı hazırlayın."
        else:
            return "Risk seviyesi normal aralıkta. Düzenli takip edin."

