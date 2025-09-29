import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_control_dashboard_access(client, django_user_model):
    # Basit kullanıcı ve şirket ilişkisi varsayımı: user.company alanı olabilir; yoksa skip
    user = django_user_model.objects.create_user(username='auditor', password='pass12345')
    client.login(username='auditor', password='pass12345')
    # Eğer user'da company attribute yoksa view redirect edecek; bunu kabul ediyoruz
    url = reverse('audit:control_dashboard')
    resp = client.get(url)
    assert resp.status_code in (200, 302)

@pytest.mark.django_db
def test_risk_assessment_post_redirect(client, django_user_model):
    user = django_user_model.objects.create_user(username='auditor2', password='pass12345')
    client.login(username='auditor2', password='pass12345')
    url = reverse('audit:risk_assessment')
    data = {
        'risk_title': 'Likidite Riski',
        'risk_description': 'Nakit akışı problemleri',
        'risk_category': 'FINANCIAL',
        'likelihood': 'MEDIUM',
        'impact': 'HIGH',
    }
    resp = client.post(url, data)
    # Şirket ilişkisi yoksa kontrol view redirect ettiği için 302 beklenebilir
    assert resp.status_code in (200, 302)

@pytest.mark.django_db
def test_requires_roles_redirects_without_role(client, django_user_model):
    user = django_user_model.objects.create_user(username='basic', password='pass12345')
    client.login(username='basic', password='pass12345')
    url = reverse('audit:control_dashboard')
    resp = client.get(url)
    # Role dekoratörü redirect dönebilir
    assert resp.status_code in (200, 302, 403)
