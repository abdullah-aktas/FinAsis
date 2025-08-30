from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, Company

# Create your tests here.

class AccountsTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Şirketi")
        self.user = CustomUser.objects.create_user(username="testuser", password="testpass123", company=self.company)
        self.client = Client()

    def test_login(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'testuser', 'password': 'testpass123'})
        self.assertIn(response.status_code, [200, 302])

    def test_profile_access(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:user_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_company_creation(self):
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(self.company.name, "Test Şirketi")

    def test_register(self):
        response = self.client.post(reverse('accounts:register'), {'username': 'newuser', 'password1': 'testpass123', 'password2': 'testpass123'})
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_company_edit(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:company_edit'), {'name': 'Yeni Şirket', 'sector': 'Teknoloji', 'tax_number': '1234567890'})
        self.assertIn(response.status_code, [200, 302])
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Yeni Şirket')

    def test_user_settings_update(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('accounts:user_settings'), {'email_notifications': '1', 'dark_mode': '1'})
        self.assertIn(response.status_code, [200, 302])
        self.user.refresh_from_db()
        self.assertTrue(self.user.settings.email_notifications)
        self.assertTrue(self.user.settings.dark_mode)
