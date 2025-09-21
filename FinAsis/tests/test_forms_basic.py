import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestPublicForms:
    def test_contact_get(self, client):
        resp = client.get(reverse('contact'))
        assert resp.status_code == 200

    def test_corporate_offer_get(self, client):
        resp = client.get(reverse('corporate-offer'))
        assert resp.status_code == 200
