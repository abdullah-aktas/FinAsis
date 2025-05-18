# -*- coding: utf-8 -*-
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import UserPreference, AIInsight, UserInteraction
from ..services import RecommendationService
from unittest.mock import patch, MagicMock

User = get_user_model()

@pytest.mark.asyncio
class TestRecommendationService(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.user_preferences = UserPreference.objects.create(
            user=self.user,
            risk_tolerance='medium',
            investment_horizon='long',
            language='tr'
        )
        
        self.service = RecommendationService()
        
    async def test_generate_recommendations(self):
        """Öneri üretme testleri"""
        context = {
            'portfolio_value': 100000,
            'risk_level': 'medium',
            'investment_goals': ['retirement', 'growth']
        }
        
        # Mock OpenAI yanıtı
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="""
            Portföy Optimizasyonu:
            - Hisse senetleri ağırlığını %60'a çıkarın
            - Tahvil pozisyonunu %30'a düşürün
            - Altın pozisyonunu %10'da tutun
            
            Yatırım Fırsatları:
            - Teknoloji sektöründe alım fırsatı
            - Temettü verimliliği yüksek hisseler
            - Yenilenebilir enerji yatırımları
            """))
        ]
        
        with patch('openai.OpenAI.chat.completions.create', return_value=mock_response):
            recommendations = await self.service.generate_recommendations(self.user, context)
            
            # Önerilerin doğru formatta olduğunu kontrol et
            assert len(recommendations) > 0
            assert all(isinstance(r, dict) for r in recommendations)
            assert all('title' in r for r in recommendations)
            assert all('recommendations' in r for r in recommendations)
            assert all('category' in r for r in recommendations)
            assert all('priority' in r for r in recommendations)
            
            # AI İçgörülerinin oluşturulduğunu kontrol et
            insights = AIInsight.objects.filter(user=self.user)
            assert insights.count() == len(recommendations)
    
    def test_recommendation_categorization(self):
        """Öneri kategorizasyon testleri"""
        test_cases = [
            ('Portföy Dağılımı', 'portfolio'),
            ('Yatırım Fırsatları', 'investment'),
            ('Risk Yönetimi', 'risk'),
            ('Vergi Optimizasyonu', 'tax'),
            ('Piyasa Görünümü', 'market'),
            ('Diğer Öneriler', 'other')
        ]
        
        for title, expected_category in test_cases:
            category = self.service._categorize_recommendation(title)
            assert category == expected_category
    
    def test_priority_calculation(self):
        """Öncelik hesaplama testleri"""
        test_cases = [
            ({
                'title': 'Acil Satış Önerisi',
                'recommendations': ['Yüksek risk tespit edildi']
            }, 'urgent'),
            ({
                'title': 'Yatırım Fırsatı',
                'recommendations': ['Yüksek getiri potansiyeli']
            }, 'high'),
            ({
                'title': 'Genel Değerlendirme',
                'recommendations': ['Normal piyasa koşulları']
            }, 'medium')
        ]
        
        for rec, expected_priority in test_cases:
            priority = self.service._calculate_priority(rec['title'], rec['recommendations'])
            assert priority == expected_priority
    
    def test_action_requirement(self):
        """Aksiyon gereksinimi testleri"""
        test_cases = [
            ({
                'title': 'Portföy Değişikliği',
                'recommendations': ['Hisseleri satın']
            }, True),
            ({
                'title': 'Piyasa Analizi',
                'recommendations': ['Trend devam ediyor']
            }, False)
        ]
        
        for rec, expected_result in test_cases:
            requires_action = self.service._requires_action(rec)
            assert requires_action == expected_result
    
    async def test_recommendation_persistence(self):
        """Öneri kaydetme testleri"""
        recommendation = {
            'title': 'Test Önerisi',
            'recommendations': ['Öneri 1', 'Öneri 2'],
            'category': 'investment',
            'priority': 'high'
        }
        
        await self.service._save_recommendations(self.user, [recommendation])
        
        # Kaydedilen içgörüyü kontrol et
        insight = AIInsight.objects.filter(user=self.user).first()
        assert insight is not None
        assert insight.title == recommendation['title']
        assert insight.priority == recommendation['priority']
        assert insight.insight_type == 'recommendation'
    
    def test_prompt_generation(self):
        """Prompt oluşturma testleri"""
        context = {'test': 'data'}
        prompt = self.service._create_enhanced_recommendation_prompt(
            user_preferences=self.user_preferences,
            market_data='test market data',
            portfolio_data='test portfolio data',
            context=context
        )
        
        # Prompt'un gerekli bileşenleri içerdiğini kontrol et
        assert 'KULLANICI PROFİLİ' in prompt
        assert 'PİYASA DURUMU' in prompt
        assert 'PORTFÖY BİLGİLERİ' in prompt
        assert 'MEVCUT DURUM' in prompt 