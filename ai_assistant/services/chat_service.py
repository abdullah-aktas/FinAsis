import logging
from typing import Dict, Any
from django.contrib.auth.models import User
from ..models import UserInteraction, AIModel
import openai
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ChatAIService:
    def __init__(self):
        """AI sohbet servisi başlatıcı"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY ortam değişkeni ayarlanmamış")
            
        openai.api_key = self.api_key
        
    def get_response(self, user: User, query: str) -> str:
        """
        Kullanıcı sorgusuna yanıt verir
        
        Args:
            user (User): Kullanıcı nesnesi
            query (str): Kullanıcı sorgusu
            
        Returns:
            str: AI yanıtı
        """
        try:
            # AI modelini al
            model = AIModel.objects.get(name='gpt-3.5-turbo')
            
            # Sohbet geçmişini al
            history = UserInteraction.objects.filter(
                user=user,
                model=model
            ).order_by('-created_at')[:5]
            
            # Sohbet mesajlarını hazırla
            messages = [
                {"role": "system", "content": "Sen finansal konularda uzmanlaşmış bir AI asistanısın."}
            ]
            
            # Geçmiş mesajları ekle
            for interaction in reversed(history):
                messages.append({"role": "user", "content": interaction.query})
                messages.append({"role": "assistant", "content": interaction.response})
                
            # Yeni sorguyu ekle
            messages.append({"role": "user", "content": query})
            
            # OpenAI API'yi çağır
            response = openai.ChatCompletion.create(
                model=model.name,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Yanıtı al
            ai_response = response.choices[0].message.content
            
            # Etkileşimi kaydet
            UserInteraction.objects.create(
                user=user,
                model=model,
                query=query,
                response=ai_response,
                parameters={
                    'temperature': 0.7,
                    'max_tokens': 1000
                }
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI sohbet hatası: {str(e)}")
            raise 