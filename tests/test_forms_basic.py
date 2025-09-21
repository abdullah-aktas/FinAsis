import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestPublicForms:
    def test_contact_get(self, client):
        resp = client.get(reverse('contact'))
        assert resp.status_code == 200
        assert b'\xc4\xb0leti\xc5\x9fim' in resp.content or b'Contact' in resp.content

    def test_contact_post(self, client):
        resp = client.post(reverse('contact'), data={
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Hello there',
        }, follow=True)
        assert resp.status_code == 200
        # Check message presence
        assert b'Te\xc5\x9fekk\xc3\xbcrler' in resp.content or b'Mesaj\xc4\xb1n\xc4\xb1z al\xc4\xb1nd\xc4\xb1' in resp.content

    def test_corporate_offer_get(self, client):
        resp = client.get(reverse('corporate-offer'))
        assert resp.status_code == 200
        assert b'Kurumsal' in resp.content

    def test_corporate_offer_post(self, client):
        resp = client.post(reverse('corporate-offer'), data={
            'company': 'Acme Inc',
            'email': 'sales@acme.test',
            'phone': '+90 555 555 55 55',
            'message': 'Teklif istiyoruz',
        }, follow=True)
        assert resp.status_code == 200
        assert b'Talebiniz al\xc4\xb1nd\xc4\xb1' in resp.content
