# -*- coding: utf-8 -*-
import json
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_recommendation_api_basic(client):
    User = get_user_model()
    user = User.objects.create_user(username='rec_user', password='x')
    client.force_login(user)
    url = reverse('ai_assistant:ml-recommendation')
    payload = {
        'income': 10000,
        'expenses': 7000,
        'savings': 1500,
        'goals': 'savings',
    }
    resp = client.post(url, data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    data = resp.json()
    assert 'recommendations' in data
    assert isinstance(data['recommendations'], list)
    assert any('title' in r for r in data['recommendations'])