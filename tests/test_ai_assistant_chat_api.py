# -*- coding: utf-8 -*-
import os
import json
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_ai_assistant_chat_endpoint_mock_mode(client, settings, monkeypatch):
    # Force mock mode so no real API call is needed
    monkeypatch.setenv('FINASIS_AI_MOCK', '1')

    User = get_user_model()
    user = User.objects.create_user(username='tester', password='x')
    client.force_login(user)

    url = reverse('ai_assistant:ai-assistant-chat')
    resp = client.post(url, data=json.dumps({'message': 'Nakit akışı nedir?'}), content_type='application/json')
    assert resp.status_code == 200
    data = resp.json()
    assert 'response' in data
    assert isinstance(data['response'], str)
