# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import UserProfile, UserPreferences, UserActivity, UserNotification, UserSession
from .serializers import UserSerializer, UserProfileSerializer, UserPreferencesSerializer

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

    def test_user_creation(self):
        """Kullanıcı oluşturma testi"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)

    def test_admin_creation(self):
        """Admin kullanıcı oluşturma testi"""
        self.assertEqual(self.admin.email, 'admin@example.com')
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)

    def test_profile_creation(self):
        """Profil otomatik oluşturma testi"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_preferences_creation(self):
        """Tercihler otomatik oluşturma testi"""
        self.assertTrue(hasattr(self.user, 'preferences'))
        self.assertIsInstance(self.user.preferences, UserPreferences)

class UserAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )

    def test_user_registration(self):
        """Kullanıcı kayıt testi"""
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_user_login(self):
        """Kullanıcı giriş testi"""
        url = reverse('user-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_user_profile_update(self):
        """Profil güncelleme testi"""
        self.client.force_authenticate(user=self.user)
        url = reverse('profile-detail', args=[self.user.profile.id])
        data = {
            'phone': '+905551234567',
            'city': 'İstanbul',
            'country': 'TR'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '+905551234567')

    def test_password_change(self):
        """Şifre değiştirme testi"""
        self.client.force_authenticate(user=self.user)
        url = reverse('password-change')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password('newpass123'))

class UserActivityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_activity_creation(self):
        """Aktivite kaydı oluşturma testi"""
        activity = UserActivity.objects.create(
            user=self.user,
            action='test_action',
            details='Test activity details'
        )
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.action, 'test_action')

    def test_activity_auto_timestamp(self):
        """Aktivite zaman damgası testi"""
        activity = UserActivity.objects.create(
            user=self.user,
            action='test_action',
            details='Test activity details'
        )
        self.assertIsNotNone(activity.created_at)

class UserNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_notification_creation(self):
        """Bildirim oluşturma testi"""
        notification = UserNotification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test notification message',
            type='info'
        )
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.is_read)

    def test_notification_mark_as_read(self):
        """Bildirimi okundu olarak işaretleme testi"""
        notification = UserNotification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test notification message',
            type='info'
        )
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)

class UserSessionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_session_creation(self):
        """Oturum oluşturma testi"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='testsessionkey',
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.session_key, 'testsessionkey')

    def test_session_last_activity(self):
        """Oturum son aktivite testi"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='testsessionkey',
            ip_address='127.0.0.1',
            user_agent='Test User Agent'
        )
        old_activity = session.last_activity
        session.save()
        self.assertNotEqual(old_activity, session.last_activity) 