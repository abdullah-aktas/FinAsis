import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounting.models import Company, Invoice


@pytest.mark.django_db
def test_admin_dashboard_access(client):
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="1234", is_staff=True)
    client.force_login(admin)
    response = client.get(reverse("management:admin_dashboard"))
    assert response.status_code == 200
    assert "Yönetim Paneli" in response.content.decode()


@pytest.mark.django_db
def test_user_list_access(client):
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="1234", is_staff=True)
    client.force_login(admin)
    response = client.get(reverse("management:user_list"))
    assert response.status_code == 200
    assert "Kullanıcı Listesi" in response.content.decode()


@pytest.mark.django_db
def test_user_bulk_delete(client):
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="1234", is_staff=True)
    user1 = User.objects.create_user(username="user1", password="1234")
    user2 = User.objects.create_user(username="user2", password="1234")
    client.force_login(admin)
    response = client.post(
        reverse("management:user_list"), {"selected_users": [user1.id, user2.id]}
    )
    assert response.status_code == 302  # Redirect
    assert not User.objects.filter(username="user1").exists()
    assert not User.objects.filter(username="user2").exists()


@pytest.mark.django_db
def test_invoice_list_access(client):
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="1234", is_staff=True)
    client.force_login(admin)
    response = client.get(reverse("management:invoice_list"))
    assert response.status_code == 200
    assert "Fatura Listesi" in response.content.decode()


@pytest.mark.django_db
def test_invoice_bulk_delete(client):
    User = get_user_model()
    admin = User.objects.create_user(username="admin", password="1234", is_staff=True)
    company = Company.objects.create(name="TestCo", sector="IT", tax_number="123")
    # Create a customer for the invoice
    from accounting.models import Customer

    customer = Customer.objects.create(
        first_name="Test", last_name="Customer", company=company
    )
    invoice1 = Invoice.objects.create(
        company=company,
        customer=customer,
        total_amount=100,
        issue_date="2024-06-01",
        due_date="2024-06-10",
        description="Test1",
    )
    invoice2 = Invoice.objects.create(
        company=company,
        customer=customer,
        total_amount=200,
        issue_date="2024-06-02",
        due_date="2024-06-12",
        description="Test2",
    )
    client.force_login(admin)
    response = client.post(
        reverse("management:invoice_list"),
        {"selected_invoices": [invoice1.id, invoice2.id]},
    )
    assert response.status_code == 302
    assert not Invoice.objects.filter(id=invoice1.id).exists()
    assert not Invoice.objects.filter(id=invoice2.id).exists()
