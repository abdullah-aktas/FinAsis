import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_ai_assistant_home_accessible(client):
    url = reverse('ai_assistant:home')
    resp = client.get(url)
    assert resp.status_code == 200, resp.content[:200]
    assert b'AI Asistan' in resp.content or b'AI Finans Asistan' in resp.content
