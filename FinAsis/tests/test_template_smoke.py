import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db

# Basit URL'ler için 200/302 smoke testi
PUBLIC_URLS = [
    '/',
    '/products/finans/',
    '/products/egitim/',
    '/products/oyunlar/',
    '/pricing/',
]

@pytest.mark.parametrize('url', PUBLIC_URLS)
def test_public_pages_render(client, url):
    resp = client.get(url)
    # Bazı sayfalar login yönlendirmesi (302) verebilir; en azından hata olmamalı
    assert resp.status_code in (200, 301, 302)
