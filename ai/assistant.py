from django.conf import settings
from transformers import pipeline
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AIAssistant:
    def __init__(self):
        self.nlp = pipeline("text-classification", model="dbmdz/bert-base-turkish-cased")
        self.qa = pipeline("question-answering", model="dbmdz/bert-base-turkish-cased")
        self.sentiment = pipeline("sentiment-analysis", model="dbmdz/bert-base-turkish-cased")
        
    def analyze_financial_text(self, text):
        """
        Finansal metin analizi
        """
        try:
            sentiment = self.sentiment(text)[0]
            classification = self.nlp(text)[0]
            
            return {
                'sentiment': sentiment['label'],
                'confidence': sentiment['score'],
                'category': classification['label'],
                'category_confidence': classification['score']
            }
        except Exception as e:
            logger.error(f"Finansal metin analizi hatası: {str(e)}")
            raise
            
    def answer_financial_question(self, question, context):
        """
        Finansal soru-cevap
        """
        try:
            result = self.qa(question=question, context=context)
            return {
                'answer': result['answer'],
                'confidence': result['score'],
                'start': result['start'],
                'end': result['end']
            }
        except Exception as e:
            logger.error(f"Finansal soru-cevap hatası: {str(e)}")
            raise
            
    def predict_financial_trends(self, data):
        """
        Finansal trend tahmini
        """
        try:
            # Veri ön işleme
            processed_data = self._preprocess_data(data)
            
            # Trend analizi
            trend = self._analyze_trend(processed_data)
            
            return {
                'trend': trend['direction'],
                'confidence': trend['confidence'],
                'prediction': trend['prediction']
            }
        except Exception as e:
            logger.error(f"Finansal trend tahmini hatası: {str(e)}")
            raise
            
    def _preprocess_data(self, data):
        """
        Veri ön işleme
        """
        # Veri temizleme ve dönüştürme işlemleri
        return data
        
    def _analyze_trend(self, data):
        """
        Trend analizi
        """
        # Trend analizi algoritması
        return {
            'direction': 'up',
            'confidence': 0.85,
            'prediction': 'Yükseliş trendi devam edecek'
        } 