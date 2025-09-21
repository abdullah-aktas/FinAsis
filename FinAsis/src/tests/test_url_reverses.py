import pytest
from django.urls import reverse, NoReverseMatch

# Temel kritik namespace + isim kombinasyonları
URL_NAMES = [
    ('finance', 'finance_home', []),
    ('virtual_company', 'virtual_company_list', []),
    ('virtual_company', 'virtual_company_create', []),
    ('ai_assistant', 'home', []),
    ('games', 'games_index', []),
    ('accounts', 'login', []),  # auth include olmadan namespace olabilir (gerekirse skip)
]

@pytest.mark.django_db
@pytest.mark.parametrize('namespace,name,args', URL_NAMES)
def test_reverse_names(namespace, name, args):
    full_name = f"{namespace}:{name}" if namespace else name
    try:
        url = reverse(full_name, args=args)
        assert url, f"Boş URL döndü: {full_name}"
    except NoReverseMatch as e:
        pytest.fail(f"Reverse başarısız: {full_name} -> {e}")
