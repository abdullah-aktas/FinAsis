# -*- coding: utf-8 -*-
import io
from unittest.mock import patch
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_ocr_upload_view_get_200(client, django_user_model):
    user = django_user_model.objects.create_user(username='viewer', password='p')
    client.login(username='viewer', password='p')
    url = reverse('ai_assistant:ocr')
    resp = client.get(url)
    assert resp.status_code == 200
    assert 'Fatura OCR' in resp.content.decode('utf-8')

@pytest.mark.django_db
def test_ocr_process_api_success(client, django_user_model):
    # Create and login user
    user = django_user_model.objects.create_user(username='u', password='p')
    client.login(username='u', password='p')

    url = reverse('ai_assistant:ocr_process_api')
    fake_image = io.BytesIO(b'fake-image-bytes')
    fake_image.name = 'invoice.jpg'

    with patch('src.apps.ai_assistant.views.OCRService.process_invoice') as mock_proc:
        mock_proc.return_value = {
            'invoice_number': 'INV-001',
            'date': '2025-10-10',
            'total': '1.234,56 TL',
            'tax_rate': '18',
            'company_name': 'FinAsis'
        }
        resp = client.post(url, {'file': fake_image})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is True
        assert 'data' in data
        assert data['data']['invoice_number'] == 'INV-001'

@pytest.mark.django_db
def test_ocr_process_api_error_from_service(client, django_user_model):
    user = django_user_model.objects.create_user(username='u2', password='p')
    client.login(username='u2', password='p')
    url = reverse('ai_assistant:ocr_process_api')
    fake_image = io.BytesIO(b'fake-image-bytes')
    fake_image.name = 'invoice.jpg'

    with patch('src.apps.ai_assistant.views.OCRService.process_invoice') as mock_proc:
        mock_proc.return_value = {'error': 'Engine missing'}
        resp = client.post(url, {'file': fake_image})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is False
        assert data.get('error') == 'Engine missing'

@pytest.mark.django_db
def test_ocr_process_api_missing_file(client, django_user_model):
    user = django_user_model.objects.create_user(username='u3', password='p')
    client.login(username='u3', password='p')
    url = reverse('ai_assistant:ocr_process_api')
    resp = client.post(url, {})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('success') is False
    assert 'Dosya yüklenmedi' in data.get('error', '')
