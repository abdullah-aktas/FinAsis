# -*- coding: utf-8 -*-
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinAsis.settings')
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestMLApi:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='mltest', password='mltest123')
        self.client.force_authenticate(user=self.user)

    def test_risk_score_success(self):
        url = '/ai-assistant/ml/risk-score/'
        data = {
            'features': [5.0, 2, 2500.0, 10, 15, 0.3]
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        result = response.json()
        assert 'risk_score' in result
        assert 0 <= result['risk_score'] <= 1
        # Model meta verisi kontrolü
        assert 'model_version' in result
        assert 'model_parameters' in result
        assert isinstance(result['model_parameters'], dict)

    def test_risk_score_invalid_data(self):
        url = '/ai-assistant/ml/risk-score/'
        data = {'features': 'notalist'}
        response = self.client.post(url, data, format='json')
        assert response.status_code == 400
        assert 'error' in response.data

    def test_financial_forecast_success(self):
        url = '/ai-assistant/ml/financial-forecast/'
        data = {
            'data': [
                {'ds': '2024-01-01', 'y': 1000},
                {'ds': '2024-01-02', 'y': 1200},
                {'ds': '2024-01-03', 'y': 1100},
            ],
            'periods': 10
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        result = response.json()
        assert 'dates' in result and 'predictions' in result
        # Model meta verisi kontrolü
        assert 'model_version' in result
        assert 'model_parameters' in result
        assert isinstance(result['model_parameters'], dict)
        # Prophet explanation alanı kontrolü
        assert 'explanation' in result
        explanation = result['explanation']
        assert 'features' in explanation and isinstance(explanation['features'], list)
        assert 'summary' in explanation and isinstance(explanation['summary'], str)

    def test_financial_forecast_invalid_data(self):
        url = '/ai-assistant/ml/financial-forecast/'
        data = {'history': 'notalist'}
        response = self.client.post(url, data, format='json')
        assert response.status_code == 400
        assert 'error' in response.data

    def test_recommendation_success(self):
        url = '/ai-assistant/ml/recommendation/'
        data = {
            'income': 5000,
            'expenses': 3000,
            'savings': 1000,
            'goals': 'investment'
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200
        result = response.json()
        assert 'recommendation' in result
        # Model meta verisi kontrolü
        assert 'model_version' in result
        assert 'model_parameters' in result
        assert isinstance(result['model_parameters'], dict)

    def test_recommendation_invalid_data(self):
        url = '/ai-assistant/ml/recommendation/'
        data = {'income': None}
        response = self.client.post(url, data, format='json')
        assert response.status_code == 200 or response.status_code == 400
        # Hatalı veri için ya öneri dönmez ya da hata mesajı döner
        assert 'recommendation' in response.data or 'error' in response.data 