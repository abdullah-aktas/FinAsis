# -*- coding: utf-8 -*-
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
                messages.append({"role": "user", "content": interaction.content})
                messages.append({"role": "assistant", "content": interaction.ai_response})
                
            # Yeni sorguyu ekle
            messages.append({"role": "user", "content": query})
            
            # OpenAI API'yi çağır
            response = openai.chat.completions.create(
                model=model.name,
                messages=messages,  # type: ignore
                temperature=0.7,
                max_tokens=1000
            )
            
            # Yanıtı al
            ai_response = response.choices[0].message.content if response.choices and response.choices[0].message and response.choices[0].message.content else ""
            
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

    def get_suggestion(self, user_input):
        # Basit öneri fonksiyonu, OpenAI ile entegre edilebilir veya stub dönebilir
        return f"AI önerisi: {user_input} için örnek öneri."

    def chat(self, message):
        # Basit sohbet fonksiyonu, OpenAI ile entegre edilebilir veya stub dönebilir
        return f"AI: {message} mesajını aldım. Size nasıl yardımcı olabilirim?" 