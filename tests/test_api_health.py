import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_api_health(client):
    resp = client.get('/api/v1/health/')
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('status') == 'ok'
    assert data.get('version') == 'v1'
