import pytest
from django.urls import reverse
from src.apps.accounts.models import CustomUser, UserType, SubscriptionType


@pytest.mark.django_db
def test_successful_registration(client):
    # Gerekli user_type ve subscription tipini hazırlayalım (opsiyonel)
    sub_type = SubscriptionType.objects.create(code='basic', name='Basic')
    utype = UserType.objects.create(code='kobi', name='Kobi', default_subscription=sub_type)

    url = reverse('accounts:register')
    resp = client.post(url, data={
        'username': 'yeniuser',
        'email': 'yeni@example.com',
        'password1': 'GucLuSifre123',
        'password2': 'GucLuSifre123',
        'user_type': utype.id,
        'new_company_name': 'Test Sirket',
        'new_company_tax_number': '1234567890'
    })
    # Başarılı ise redirect bekleriz
    assert resp.status_code in (302, 303)
    assert CustomUser.objects.filter(username='yeniuser').exists()
    user = CustomUser.objects.get(username='yeniuser')
    assert user.company is not None
    assert user.user_type == utype
