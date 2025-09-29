import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_modules_overview_requires_login(client):
    url = reverse('admin:modules_overview')
    resp = client.get(url)
    # Django admin redirects to login with next parameter
    assert resp.status_code in (301, 302)
    assert 'login' in resp.headers.get('Location','')

@pytest.mark.django_db
def test_modules_overview_superuser(admin_client):
    url = reverse('admin:modules_overview')
    resp = admin_client.get(url)
    assert resp.status_code == 200
    # Basic content checks
    assert 'Modül Yönetimi' in resp.content.decode('utf-8')
    # Expect at least one project app label to appear
    assert 'accounts' in resp.content.decode('utf-8') or 'finance' in resp.content.decode('utf-8')
