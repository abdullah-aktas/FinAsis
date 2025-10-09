import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.utils import CaptureQueriesContext
from django.db import connection
from src.apps.accounting.models import Company, BankAccount, BankTransaction


@pytest.mark.django_db
def test_banktransactions_list_nplus1_guard(client):
    User = get_user_model()
    company = Company.objects.create(name='N1 Co', tax_number='1234567890')
    user = User.objects.create_user(username='n1user', password='pass12345', company=company)
    # 1 hesap, çok sayıda hareket
    acc = BankAccount.objects.create(company=company, bank_name='X', iban='TR100000000000000000000000', account_name='N1', account_type='VADESIZ')
    for i in range(10):
        BankTransaction.objects.create(account=acc, amount=10 + i, transaction_type='IN')

    assert client.login(username='n1user', password='pass12345')
    url = reverse('accounting:api_banktransactions-list')

    with CaptureQueriesContext(connection) as ctx:
        resp = client.get(url)
    assert resp.status_code == 200
    # Guard: 10 kayıt için 20'den az sorgu bekleyelim (select_related var)
    assert len(ctx.captured_queries) < 20, f"Too many queries: {len(ctx.captured_queries)}"