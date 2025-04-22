import openai
from langchain import LLMChain, PromptTemplate
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from django.conf import settings
from .models import AIModel, UserInteraction, FinancialPrediction
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class BaseAIService:
    """Temel AI servisi sınıfı"""
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def _preprocess_data(self, data):
        """Veri ön işleme"""
        try:
            if isinstance(data, pd.DataFrame):
                return self.scaler.fit_transform(data)
            return self.scaler.fit_transform(np.array(data).reshape(-1, 1))
        except Exception as e:
            logger.error(f"Veri ön işleme hatası: {str(e)}")
            raise
            
    def _log_interaction(self, user, interaction_type, query, response, processing_time):
        """Kullanıcı etkileşimini kaydet"""
        try:
            UserInteraction.objects.create(
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