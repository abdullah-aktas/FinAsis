# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
import json
import time

class TestAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cache.clear()

    def test_home_view(self):
        response = self.client.get(reverse('testapp:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FinAsis Test Sayfası")

    def test_test_view(self):
        response = self.client.get(reverse('testapp:test'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

    def test_protected_test_view(self):
        # Giriş yapmadan erişim
        response = self.client.get(reverse('testapp:protected_test'))
        self.assertEqual(response.status_code, 302)  # Yönlendirme

        # Giriş yaparak erişim
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('testapp:protected_test'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

    def test_api_test_view(self):
        test_data = {'test': 'data'}
        response = self.client.post(
            reverse('testapp:api_test'),
            data=json.dumps(test_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['received_data'], test_data)

    def test_health_check(self):
        response = self.client.get(reverse('testapp:health_check'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')

    def test_performance_test(self):
        start_time = time.time()
        response = self.client.get(reverse('testapp:performance_test'))
        execution_time = time.time() - start_time

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertLess(execution_time, 1.0)  # 1 saniyeden az sürmeli

    def test_cache_mechanism(self):
        # İlk istek
        response1 = self.client.get(reverse('testapp:test'))
        data1 = json.loads(response1.content)
        
        # İkinci istek (cache'den gelmeli)
        response2 = self.client.get(reverse('testapp:test'))
        data2 = json.loads(response2.content)
        
        self.assertEqual(data1, data2) 