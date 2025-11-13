# -*- coding: utf-8 -*-
from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from virtual_company.models import VirtualCompany, Product

User = get_user_model()

# Create your tests here.

@pytest.mark.django_db
def test_virtual_company_create():
    user = User.objects.create_user('testuser', 'test@example.com', 'pass')
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('company-list')
    data = {
        'name': 'Test Şirket',
        'description': 'Açıklama'
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert response.data['name'] == 'Test Şirket'

@pytest.mark.django_db
def test_product_create():
    user = User.objects.create_user('testuser2', 'test2@example.com', 'pass')
    company = VirtualCompany.objects.create(name='Şirket', description='desc', owner=user)
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('product-list')
    data = {
        'name': 'Test Ürün',
        'description': 'Ürün açıklaması',
        'price': '10.00',
        'stock': 5
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert response.data['name'] == 'Test Ürün'
