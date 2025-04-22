import openai
from langchain import LLMChain, PromptTemplate
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from django.conf import settings
from .models import AIModel, UserInteraction, FinancialPrediction, UserPreference, AIInsight
from typing import Dict, List, Any
from django.core.cache import cache
from asgiref.sync import sync_to_async
import asyncio
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
import hashlib
import hmac
import random

logger = logging.getLogger(__name__)

class SecurityMixin:
    """Güvenlik kontrolleri için mixin"""
    
    def __init__(self):
        self.max_requests_per_minute = 60
        self.request_timeout = 30
        self.max_content_length = 1024 * 1024  # 1MB
        
    def _validate_request(self, user, data):
        """İstek doğrulama"""
        # Rate limiting kontrolü
        cache_key = f"request_count_{user.id}"
        request_count = cache.get(cache_key, 0)
        
        if request_count >= self.max_requests_per_minute:
            raise ValidationError("Çok fazla istek gönderildi. Lütfen biraz bekleyin.")
            
        cache.incr(cache_key)
        cache.expire(cache_key, 60)  # 1 dakika
        
        # İçerik boyutu kontrolü
        if len(str(data)) > self.max_content_length:
            raise ValidationError("İçerik boyutu çok büyük.")
            
    def _generate_request_signature(self, data):
        """İstek imzası oluştur"""
        secret = settings.AI_REQUEST_SECRET
        message = str(data).encode()
        signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
        return signature
        
    def _verify_request_signature(self, data, signature):
        """İstek imzası doğrula"""
        expected_signature = self._generate_request_signature(data)
        return hmac.compare_digest(signature, expected_signature)

class BaseAIService(SecurityMixin):
    """Temel AI servisi sınıfı"""
    def __init__(self):
        super().__init__()
        self.model = None
        self.scaler = StandardScaler()
        self.cache_timeout = 3600  # 1 saat
        
    async def process_request(self, user, data, signature=None):
        """İstek işleme"""
        try:
            # Güvenlik kontrolleri
            self._validate_request(user, data)
            if signature and not self._verify_request_signature(data, signature):
                raise ValidationError("Geçersiz istek imzası.")
                
            # Veri işleme
            processed_data = await self._preprocess_data(data)
            return processed_data
            
        except Exception as e:
            logger.error(f"İstek işleme hatası: {str(e)}")
            raise
        
    async def _preprocess_data(self, data):
        """Veri ön işleme"""
        cache_key = f"preprocessed_data_{hash(str(data))}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
            
        try:
            if isinstance(data, pd.DataFrame):
                result = await sync_to_async(self.scaler.fit_transform)(data)
            else:
                result = await sync_to_async(self.scaler.fit_transform)(np.array(data).reshape(-1, 1))
            
            cache.set(cache_key, result, self.cache_timeout)
            return result
        except Exception as e:
            logger.error(f"Veri ön işleme hatası: {str(e)}")
            raise
            
    async def _log_interaction(self, user, interaction_type, query, response, processing_time):
        """Kullanıcı etkileşimini kaydet"""
        try:
            await sync_to_async(UserInteraction.objects.create)(
                user=user,
                interaction_type=interaction_type,
                query=query,
                response=response,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Etkileşim kaydı hatası: {str(e)}")

class FinancialAIService(BaseAIService):
    """Finansal AI analiz servisi"""
    
    def __init__(self):
        super().__init__()
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.market_model = self._load_market_model()
        self.risk_model = self._load_risk_model()
        
    def _load_market_model(self):
        """Piyasa tahmin modelini yükle"""
        try:
            model_obj = AIModel.objects.get(model_type='financial', is_active=True)
            model = GradientBoostingRegressor(**model_obj.parameters)
            return model
        except AIModel.DoesNotExist:
            logger.warning("Aktif piyasa modeli bulunamadı, varsayılan model kullanılıyor.")
            return GradientBoostingRegressor()
            
    def _load_risk_model(self):
        """Risk analiz modelini yükle"""
        try:
            model_obj = AIModel.objects.get(model_type='risk_analysis', is_active=True)
            model = RandomForestClassifier(**model_obj.parameters)
            return model
        except AIModel.DoesNotExist:
            logger.warning("Aktif risk modeli bulunamadı, varsayılan model kullanılıyor.")
            return RandomForestClassifier()
    
    def analyze_financial_data(self, user, data: Dict[str, Any]) -> Dict[str, Any]:
        """Finansal veri analizi yapar"""
        try:
            # OpenAI API'sini kullanarak finansal analiz
            analysis_prompt = self._create_analysis_prompt(data)
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir finansal analiz uzmanısın."},
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            analysis_result = response.choices[0].message.content
            
            # Analiz sonuçlarını kaydet
            prediction = FinancialPrediction.objects.create(
                user=user,
                input_data=data,
                prediction_result=analysis_result
            )
            
            return {
                "analysis": analysis_result,
                "prediction_id": prediction.id
            }
            
        except Exception as e:
            logger.error(f"Finansal analiz hatası: {str(e)}")
            raise
    
    def get_personalized_recommendations(self, user, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Kişiselleştirilmiş finansal öneriler sunar"""
        try:
            # Kullanıcının geçmiş etkileşimlerini al
            user_interactions = UserInteraction.objects.filter(user=user).order_by('-created_at')[:5]
            
            # OpenAI API'sini kullanarak öneriler oluştur
            recommendation_prompt = self._create_recommendation_prompt(user_interactions, data)
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir finansal danışmansın."},
                    {"role": "user", "content": recommendation_prompt}
                ]
            )
            
            recommendations = response.choices[0].message.content
            
            return self._parse_recommendations(recommendations)
            
        except Exception as e:
            logger.error(f"Öneri oluşturma hatası: {str(e)}")
            raise
    
    def predict_market_trends(self, user, data: Dict[str, Any]) -> Dict[str, Any]:
        """Piyasa trendlerini tahmin eder"""
        try:
            # OpenAI API'sini kullanarak trend analizi
            trend_prompt = self._create_trend_prompt(data)
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir piyasa analisti ve trend uzmanısın."},
                    {"role": "user", "content": trend_prompt}
                ]
            )
            
            trends = response.choices[0].message.content
            
            return {
                "trends": self._parse_trends(trends),
                "timestamp": data.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Trend analizi hatası: {str(e)}")
            raise
    
    def _create_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Finansal analiz için prompt oluşturur"""
        return f"""
        Lütfen aşağıdaki finansal verileri analiz et:
        
        Finansal Veriler:
        {data}
        
        Şunları analiz et:
        1. Temel finansal göstergeler
        2. Risk faktörleri
        3. Fırsatlar ve tehditler
        4. Gelecek tahminleri
        """
    
    def _create_recommendation_prompt(self, interactions, data: Dict[str, Any]) -> str:
        """Öneriler için prompt oluşturur"""
        return f"""
        Kullanıcının geçmiş etkileşimleri ve mevcut verilere dayanarak
        kişiselleştirilmiş finansal öneriler oluştur:
        
        Geçmiş Etkileşimler:
        {interactions}
        
        Mevcut Veriler:
        {data}
        
        Lütfen şu alanlarda öneriler sun:
        1. Yatırım stratejileri
        2. Risk yönetimi
        3. Portföy optimizasyonu
        4. Finansal hedefler
        """
    
    def _create_trend_prompt(self, data: Dict[str, Any]) -> str:
        """Trend analizi için prompt oluşturur"""
        return f"""
        Lütfen aşağıdaki verilere dayanarak piyasa trendlerini analiz et:
        
        Piyasa Verileri:
        {data}
        
        Şunları analiz et:
        1. Kısa vadeli trendler (1-3 ay)
        2. Orta vadeli trendler (3-6 ay)
        3. Uzun vadeli trendler (6-12 ay)
        4. Risk faktörleri ve fırsatlar
        """
    
    def _parse_recommendations(self, recommendations: str) -> List[Dict[str, Any]]:
        """OpenAI yanıtını yapılandırılmış önerilere dönüştürür"""
        # Bu metod OpenAI'dan gelen metin yanıtını parse eder
        # ve yapılandırılmış bir formata dönüştürür
        # Gerçek implementasyonda daha detaylı bir parsing yapılmalı
        return [{"recommendation": r} for r in recommendations.split("\n") if r.strip()]
    
    def _parse_trends(self, trends: str) -> Dict[str, Any]:
        """OpenAI yanıtını yapılandırılmış trend analizine dönüştürür"""
        # Bu metod OpenAI'dan gelen metin yanıtını parse eder
        # ve yapılandırılmış bir formata dönüştürür
        # Gerçek implementasyonda daha detaylı bir parsing yapılmalı
        return {
            "short_term": trends.split("Kısa vadeli:")[1].split("Orta vadeli:")[0].strip(),
            "medium_term": trends.split("Orta vadeli:")[1].split("Uzun vadeli:")[0].strip(),
            "long_term": trends.split("Uzun vadeli:")[1].strip()
        }

class ChatAIService(BaseAIService):
    """AI sohbet servisi"""
    
    def __init__(self):
        super().__init__()
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.llm = LLMChain(
            prompt=PromptTemplate(
                input_variables=["query"],
                template="Sen bir finansal danışmansın. Kullanıcının sorusuna profesyonel ve detaylı bir şekilde yanıt ver: {query}"
            )
        )
        
    async def get_response(self, user, query: str) -> str:
        """Kullanıcı sorgusuna AI yanıtı üretir"""
        try:
            # Kullanıcının sohbet geçmişini al
            chat_history = UserInteraction.objects.filter(
                user=user,
                interaction_type='chat'
            ).order_by('-created_time')[:5]
            
            # OpenAI API'sini kullanarak yanıt oluştur
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir finansal danışman asistanısın."},
                    *[{"role": "user" if i % 2 == 0 else "assistant", 
                       "content": interaction.content} 
                      for i, interaction in enumerate(chat_history)],
                    {"role": "user", "content": query}
                ]
            )
            
            ai_response = response.choices[0].message.content
            
            # Etkileşimi kaydet
            UserInteraction.objects.create(
                user=user,
                interaction_type='chat',
                content=query,
                ai_response=ai_response
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Sohbet yanıtı oluşturma hatası: {str(e)}")
            raise 

class RecommendationService(BaseAIService):
    """Gelişmiş öneri sistemi"""
    
    def __init__(self):
        super().__init__()
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate_recommendations(self, user, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Kapsamlı finansal öneriler üretir"""
        try:
            # Kullanıcı tercihlerini al
            user_preferences = await sync_to_async(UserPreference.objects.get)(user=user)
            
            # Kullanıcının geçmiş etkileşimlerini al
            interactions = await sync_to_async(UserInteraction.objects.filter)(
                user=user,
                interaction_type='recommendation'
            ).order_by('-created_at')[:10]
            
            # Piyasa verilerini al
            market_data = await self._get_market_data()
            
            # Kullanıcının portföy verilerini al
            portfolio_data = await self._get_portfolio_data(user)
            
            # OpenAI API'sini kullanarak öneriler oluştur
            prompt = self._create_enhanced_recommendation_prompt(
                user_preferences=user_preferences,
                interactions=interactions,
                market_data=market_data,
                portfolio_data=portfolio_data,
                context=context
            )
            
            response = await sync_to_async(self.openai_client.chat.completions.create)(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_recommendation_system_prompt()},
                    {"role": "user", "content": prompt}
                ]
            )
            
            recommendations = self._parse_enhanced_recommendations(response.choices[0].message.content)
            
            # Önerileri kaydet ve bildirim oluştur
            await self._save_recommendations(user, recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Öneri oluşturma hatası: {str(e)}")
            raise
    
    def _get_recommendation_system_prompt(self) -> str:
        """Sistem promptunu oluşturur"""
        return """Sen deneyimli bir finansal danışmansın. Görevin:
        1. Kullanıcının risk toleransı ve yatırım vadesine uygun öneriler sunmak
        2. Piyasa koşullarını ve trendleri analiz etmek
        3. Portföy çeşitlendirmesi ve risk yönetimi önerileri sunmak
        4. Vergi optimizasyonu ve maliyet azaltma stratejileri önermek
        5. Fırsat ve tehditleri belirlemek
        6. Somut, uygulanabilir eylem adımları sunmak
        7. Her önerinin potansiyel risk ve getirisini açıklamak"""
    
    def _create_enhanced_recommendation_prompt(self, **kwargs) -> str:
        """Gelişmiş öneri promptu oluşturur"""
        user_preferences = kwargs.get('user_preferences')
        market_data = kwargs.get('market_data')
        portfolio_data = kwargs.get('portfolio_data')
        context = kwargs.get('context')
        
        return f"""
        KULLANICI PROFİLİ:
        - Risk Toleransı: {user_preferences.risk_tolerance}
        - Yatırım Vadesi: {user_preferences.investment_horizon}
        - Tercih Edilen Dil: {user_preferences.language}
        
        PİYASA DURUMU:
        {market_data}
        
        PORTFÖY BİLGİLERİ:
        {portfolio_data}
        
        MEVCUT DURUM:
        {context}
        
        Lütfen aşağıdaki başlıklarda öneriler sun:
        1. Portföy Optimizasyonu
           - Varlık dağılımı
           - Risk yönetimi
           - Rebalancing önerileri
        
        2. Yatırım Fırsatları
           - Kısa vadeli fırsatlar
           - Orta vadeli fırsatlar
           - Uzun vadeli fırsatlar
        
        3. Risk Yönetimi
           - Stop-loss seviyeleri
           - Hedge stratejileri
           - Çeşitlendirme önerileri
        
        4. Vergi ve Maliyet Optimizasyonu
           - Vergi avantajlı yatırımlar
           - İşlem maliyetlerini azaltma
           - Vergi planlaması
        
        5. Piyasa Görünümü ve Uyarılar
           - Önemli riskler
           - Yaklaşan fırsatlar
           - Dikkat edilmesi gereken gelişmeler
        """
    
    def _parse_enhanced_recommendations(self, content: str) -> List[Dict[str, Any]]:
        """OpenAI yanıtını yapılandırılmış önerilere dönüştürür"""
        sections = content.split('\n\n')
        recommendations = []
        
        for section in sections:
            if not section.strip():
                continue
                
            # Başlığı ve içeriği ayır
            parts = section.split(':\n')
            if len(parts) != 2:
                continue
                
            title, content = parts
            
            # Alt önerileri parse et
            sub_recommendations = [
                item.strip()[2:] for item in content.split('\n')
                if item.strip().startswith('- ')
            ]
            
            recommendations.append({
                'title': title.strip(),
                'recommendations': sub_recommendations,
                'category': self._categorize_recommendation(title),
                'priority': self._calculate_priority(title, sub_recommendations)
            })
        
        return recommendations
    
    async def _save_recommendations(self, user, recommendations: List[Dict[str, Any]]):
        """Önerileri kaydeder ve bildirim oluşturur"""
        for rec in recommendations:
            # AI İçgörüsü oluştur
            insight = await sync_to_async(AIInsight.objects.create)(
                user=user,
                insight_type='recommendation',
                title=rec['title'],
                content='\n'.join(rec['recommendations']),
                priority=rec['priority'],
                action_required=self._requires_action(rec)
            )
            
            # Yüksek öncelikli öneriler için bildirim oluştur
            if rec['priority'] in ['high', 'urgent']:
                await self._create_notification(user, insight)
    
    def _categorize_recommendation(self, title: str) -> str:
        """Öneriyi kategorize eder"""
        categories = {
            'portfolio': ['portföy', 'varlık', 'dağılım'],
            'investment': ['yatırım', 'fırsat', 'alım'],
            'risk': ['risk', 'hedge', 'stop-loss'],
            'tax': ['vergi', 'maliyet', 'optimizasyon'],
            'market': ['piyasa', 'trend', 'görünüm']
        }
        
        title_lower = title.lower()
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        return 'other'
    
    def _calculate_priority(self, title: str, recommendations: List[str]) -> str:
        """Önerinin önceliğini hesaplar"""
        urgent_keywords = ['acil', 'kritik', 'önemli', 'hemen', 'risk']
        high_keywords = ['yüksek', 'fırsat', 'kazanç', 'kayıp']
        
        text = ' '.join([title] + recommendations).lower()
        
        if any(keyword in text for keyword in urgent_keywords):
            return 'urgent'
        elif any(keyword in text for keyword in high_keywords):
            return 'high'
        return 'medium'
    
    def _requires_action(self, recommendation: Dict[str, Any]) -> bool:
        """Önerinin aksiyon gerektirip gerektirmediğini belirler"""
        action_keywords = ['al', 'sat', 'değiştir', 'ayarla', 'güncelle', 'uygula']
        text = ' '.join([recommendation['title']] + recommendation['recommendations']).lower()
        return any(keyword in text for keyword in action_keywords)
    
    async def _create_notification(self, user, insight: AIInsight):
        """Bildirim oluşturur"""
        # Burada bildirim sisteminize göre implementasyon yapılmalı
        pass

    async def _get_market_data(self):
        # Bu metod, piyasa verilerini almak için uygun bir şekilde doldurulmalı
        pass

    async def _get_portfolio_data(self, user):
        # Bu metod, kullanıcının portföy verilerini almak için uygun bir şekilde doldurulmalı
        pass

def get_market_analysis():
    """
    Piyasa analizi verilerini döndürür.
    Gerçek uygulamada bu veriler harici API'lerden veya veritabanından alınacaktır.
    """
    # Örnek veriler
    trends = {
        'short_term': random.choice(['Yükseliş trendi', 'Düşüş trendi', 'Yatay hareket']),
        'medium_term': random.choice(['Pozitif', 'Nötr', 'Negatif']),
        'long_term': random.choice(['Güçlü yükseliş', 'Orta vadeli yükseliş', 'Dengeli'])
    }

    risk_indicators = {
        'volatility': random.choice(['low', 'medium', 'high']),
        'market_sentiment': random.choice(['positive', 'negative'])
    }

    return {
        'trends': trends,
        'risk_indicators': risk_indicators
    } 