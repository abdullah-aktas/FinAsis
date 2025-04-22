from django.test import TestCase
from django.utils import timezone
from ..models import User
import pyotp

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Kullanıcı oluşturma testi"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_role_assignment(self):
        """Rol atama testi"""
        self.user.role = 'admin'
        self.user.save()
        self.assertEqual(self.user.role, 'admin')
        self.assertTrue(self.user.has_role('admin'))
    
    def test_two_factor_authentication(self):
        """İki faktörlü kimlik doğrulama testi"""
        self.user.two_factor_enabled = True
        secret = self.user.generate_two_factor_secret()
        
        # Geçerli kod oluştur
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        
        # Geçersiz kod
        invalid_code = '000000'
        
        self.assertTrue(self.user.verify_two_factor_code(valid_code))
        self.assertFalse(self.user.verify_two_factor_code(invalid_code))
    
    def test_password_expiry(self):
        """Şifre süre sonu testi"""
        self.user.password_expiry_date = timezone.now() - timezone.timedelta(days=1)
        self.user.save()
        self.assertTrue(self.user.is_password_expired())
    
    def test_account_locking(self):
        """Hesap kilitleme testi"""
        self.user.failed_login_attempts = 5
        self.user.save()
        
        # Signal'ın hesabı kilitlemesini bekle
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.account_locked_until)
    
    def test_virtual_company_user(self):
        """Sanal şirket kullanıcısı testi"""
        self.user.is_virtual_company_user = True
        self.user.save()
        self.assertTrue(self.user.is_virtual_company_user)
    
    def test_user_preferences(self):
        """Kullanıcı tercihleri testi"""
        self.user.language = 'tr'
        self.user.theme = 'dark'
        self.user.notifications_enabled = False
        self.user.save()
        
        self.assertEqual(self.user.language, 'tr')
        self.assertEqual(self.user.theme, 'dark')
        self.assertFalse(self.user.notifications_enabled) 