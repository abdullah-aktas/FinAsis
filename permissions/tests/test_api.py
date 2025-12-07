import os

# pytest.ini DJANGO_SETTINGS_MODULE'i config.settings olarak ayarlar,
# fakat bu dosya bağımsız koşturulursa da aynı davranışı koruyalım.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from permissions.models import Permission

User = get_user_model()


@pytest.mark.django_db
def test_permission_create():
    user = User.objects.create_superuser("admin", "admin@example.com", "pass")
    client = APIClient()
    client.force_authenticate(user=user)
    ct = ContentType.objects.get(app_label="permissions", model="permission")
    url = reverse("permissions:api-permission-list")
    data = {
        "name": "Test Yetki",
        "codename": "test_permission",
        "content_type": ct.id,
        "description": "Test açıklama",
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert response.data["name"] == "Test Yetki"


@pytest.mark.django_db
def test_user_permission_create():
    user = User.objects.create_superuser("admin2", "admin2@example.com", "pass")
    client = APIClient()
    client.force_authenticate(user=user)
    ct = ContentType.objects.get(app_label="permissions", model="permission")
    perm = Permission.objects.create(name="Test", codename="test", content_type=ct)
    url = reverse("permissions:api-userpermission-list")
    data = {"user": user.id, "permission": perm.id}
    response = client.post(url, data)
    assert response.status_code == 201
    assert response.data["user"] == user.id
    assert response.data["permission"] == perm.id
