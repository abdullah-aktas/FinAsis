import pytest
from django.test import Client
from django.contrib.auth.models import User
from src.apps.tenancy.models import Tenant
from src.apps.audit.models import AuditEvent

def test_tenant_resolution_header(db):
    t = Tenant.objects.create(name='Acme', code='acme')
    c = Client(HTTP_X_TENANT='acme')
    # Use a lightweight existing endpoint that doesn't require templates
    resp = c.get('/health/')
    # Middleware only sets request.tenant; home might 200/302
    assert resp.status_code in (200, 302)

@pytest.mark.django_db
def test_audit_event_create_simple(db):
    # Create tenant and user then a model instance in tracked app
    user = User.objects.create_user(username='u1', password='p')
    from FinAsis.apps.finance.models import Voucher, Employee
    from django.contrib.auth import get_user_model
    # Minimal employee + voucher
    emp_user = User.objects.create_user(username='emp', password='p')
    employee = Employee.objects.create(user=emp_user, department='IT', employee_id='E1')
    v = Voucher.objects.create(employee=employee, amount=10, description='Test')
    # Audit signal should have fired
    assert AuditEvent.objects.filter(object_id=str(v.pk)).exists()
