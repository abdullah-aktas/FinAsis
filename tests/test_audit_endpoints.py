import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import connection

# Doğrudan gerçek modülleri import et (proje kökünde FinAsis paket yapısı assumed)
from src.apps.accounting.models import Company  # düzeltilen import yolu
from src.apps.finance.internal_control_system import ControlActivity, ApprovalWorkflow  # düzeltilen import yolu

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_with_company():
    # Eğer gerekli tablolar yoksa testleri atla
    tables = set(connection.introspection.table_names())
    if 'accounting_company' not in tables:
        pytest.skip('Company tablosu yok - migrations uygulanmamış.')
    User = get_user_model()
    user = User.objects.create_user(username='tester', password='pass1234')
    company = Company.objects.create(name='Test Co', tax_number='1234567890')
    setattr(user, 'company', company)
    return user


@pytest.fixture
def control(user_with_company):
    if 'finance_controlactivity' not in set(connection.introspection.table_names()):
        pytest.skip('ControlActivity tablosu yok - migrations uygulanmamış.')
    company = getattr(user_with_company, 'company')
    return ControlActivity.objects.create(
        company=company,
        control_id='CTRL-1',
        control_name='Test Control',
        control_description='Desc',
        control_objective='Obj',
        control_type='PREVENTIVE',
        control_nature='MANUAL',
        frequency='MONTHLY',
        control_owner=user_with_company,
        control_procedure='Proc',
    )


@pytest.fixture
def workflow(user_with_company):
    if 'finance_approvalworkflow' not in set(connection.introspection.table_names()):
        pytest.skip('ApprovalWorkflow tablosu yok - migrations uygulanmamış.')
    company = getattr(user_with_company, 'company')
    return ApprovalWorkflow.objects.create(company=company, name='WF1', is_active=False)


def test_control_test_all(client, user_with_company, control):
    client.force_login(user_with_company)
    url = reverse('audit:control_test_all')
    resp = client.get(url)
    assert resp.status_code in (302, 303)  # redirect back to dashboard


def test_ajax_test_control(client, user_with_company, control):
    client.force_login(user_with_company)
    url = reverse('audit:ajax_test_control', args=[control.id])
    resp = client.post(url, {'result': 'EFFECTIVE'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['success'] is True
    assert data['effectiveness'] in ('EFFECTIVE', 'INEFFECTIVE', 'NEEDS_IMPROVEMENT')
    assert 'deficiency_count' in data


def test_workflow_approve_reject(client, user_with_company, workflow):
    client.force_login(user_with_company)
    approve_url = reverse('audit:ajax_workflow_approve', args=[workflow.id])
    resp = client.post(approve_url)
    assert resp.status_code == 200
    assert resp.json()['status'] == 'active'
    reject_url = reverse('audit:ajax_workflow_reject', args=[workflow.id])
    resp2 = client.post(reject_url)
    assert resp2.status_code == 200
    assert resp2.json()['status'] == 'inactive'
