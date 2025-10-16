import os
import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_ai_chat_endpoint_authenticated_client(client, settings):
    # Force mock mode to avoid external API
    settings.SECRET_KEY = settings.SECRET_KEY or 'test'
    os.environ['FINASIS_AI_MOCK'] = '1'

    # Create and login user
    user = User.objects.create_user(username='u1', password='p1')
    client.login(username='u1', password='p1')

    url = reverse('ai_assistant:ai-assistant-chat')
    payload = {"message": "Nakit akışı nasıl iyileştirilir?", "context": {"path": "/dashboard", "title": "Panel"}}
    resp = client.post(url, data=payload, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert resp.status_code == 200
    data = resp.json()
    assert 'response' in data
    assert isinstance(data['response'], str)
    assert len(data['response']) > 0
