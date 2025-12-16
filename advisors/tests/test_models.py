# -*- coding: utf-8 -*-
"""
Mali Müşavirlik Modülü Model Testleri
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from advisors.models import (
    AdvisorProfile,
    TaxpayerProfile,
    Engagement,
    ConsultationSession,
    AdvisorReport,
    ClientContract,
    AdvisorTask,
)
from advisors.models_marketplace import (
    ConsultantProfile,
    ConsultationBooking,
    ConsultantReview,
)

User = get_user_model()


class AdvisorProfileTestCase(TestCase):
    """AdvisorProfile model testleri"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_advisor',
            email='advisor@test.com',
            password='testpass123'
        )

    def test_advisor_profile_creation(self):
        """AdvisorProfile oluşturma testi"""
        advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )
        self.assertEqual(advisor.user, self.user)
        self.assertEqual(advisor.type, 'SMMM')
        self.assertEqual(str(advisor), f"{self.user.username} (SMMM)")

    def test_advisor_profile_str(self):
        """AdvisorProfile string gösterimi"""
        advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='YMM',
            chamber_no='67890'
        )
        self.assertIn('test_advisor', str(advisor))
        self.assertIn('YMM', str(advisor))


class TaxpayerProfileTestCase(TestCase):
    """TaxpayerProfile model testleri"""

    def test_taxpayer_profile_creation(self):
        """TaxpayerProfile oluşturma testi"""
        taxpayer = TaxpayerProfile.objects.create(
            name='Test Şirketi',
            vkn_tckn='1234567890'
        )
        self.assertEqual(taxpayer.name, 'Test Şirketi')
        self.assertEqual(taxpayer.vkn_tckn, '1234567890')
        self.assertEqual(str(taxpayer), 'Test Şirketi (1234567890)')


class EngagementTestCase(TestCase):
    """Engagement model testleri"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_advisor',
            email='advisor@test.com',
            password='testpass123'
        )
        self.advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )
        self.taxpayer = TaxpayerProfile.objects.create(
            name='Test Şirketi',
            vkn_tckn='1234567890'
        )

    def test_engagement_creation(self):
        """Engagement oluşturma testi"""
        engagement = Engagement.objects.create(
            advisor=self.advisor,
            taxpayer=self.taxpayer,
            scope='both',
            status='active'
        )
        self.assertEqual(engagement.advisor, self.advisor)
        self.assertEqual(engagement.taxpayer, self.taxpayer)
        self.assertEqual(engagement.scope, 'both')
        self.assertEqual(engagement.status, 'active')

    def test_engagement_unique_together(self):
        """Engagement unique_together testi"""
        Engagement.objects.create(
            advisor=self.advisor,
            taxpayer=self.taxpayer,
            scope='defter',
            status='active'
        )
        # Aynı advisor, taxpayer ve scope ile ikinci kayıt oluşturulamaz
        with self.assertRaises(Exception):
            Engagement.objects.create(
                advisor=self.advisor,
                taxpayer=self.taxpayer,
                scope='defter',
                status='pending'
            )


class ConsultantProfileTestCase(TestCase):
    """ConsultantProfile model testleri"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_consultant',
            email='consultant@test.com',
            password='testpass123'
        )
        self.advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )

    def test_consultant_profile_creation(self):
        """ConsultantProfile oluşturma testi"""
        from decimal import Decimal
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor,
            display_name='Test Consultant',
            bio='Test bio',
            city='İstanbul',
            phone='+90 555 123 4567',
            hourly_rate=Decimal('500.00'),
            approval_status='pending'
        )
        self.assertEqual(consultant.advisor, self.advisor)
        self.assertEqual(consultant.display_name, 'Test Consultant')
        self.assertEqual(consultant.approval_status, 'pending')

    def test_consultant_is_available(self):
        """ConsultantProfile is_available testi"""
        from decimal import Decimal
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor,
            display_name='Test Consultant',
            bio='Test bio',
            city='İstanbul',
            phone='+90 555 123 4567',
            hourly_rate=Decimal('500.00'),
            approval_status='approved',
            diploma_verified=True,
            graduation_verified=True,
            availability_status='available',
            accepts_new_clients=True
        )
        # Blockchain anlaşması olmadan available değil
        self.assertFalse(consultant.is_available())
        
        consultant.blockchain_contract_address = '0x1234567890abcdef'
        consultant.save()
        self.assertTrue(consultant.is_available())

    def test_consultant_calculate_commission(self):
        """ConsultantProfile komisyon hesaplama testi"""
        from decimal import Decimal
        consultant = ConsultantProfile.objects.create(
            advisor=self.advisor,
            display_name='Test Consultant',
            bio='Test bio',
            city='İstanbul',
            phone='+90 555 123 4567',
            hourly_rate=Decimal('500.00'),
            commission_rate=Decimal('15.00')
        )
        amount = Decimal('1000.00')
        commission = consultant.calculate_commission(amount)
        self.assertEqual(commission, Decimal('150.00'))


class ConsultationBookingTestCase(TestCase):
    """ConsultationBooking model testleri"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_consultant',
            email='consultant@test.com',
            password='testpass123'
        )
        self.client_user = User.objects.create_user(
            username='test_client',
            email='client@test.com',
            password='testpass123'
        )
        self.advisor = AdvisorProfile.objects.create(
            user=self.user,
            type='SMMM',
            chamber_no='12345'
        )
        from decimal import Decimal
        self.consultant = ConsultantProfile.objects.create(
            advisor=self.advisor,
            display_name='Test Consultant',
            bio='Test bio',
            city='İstanbul',
            phone='+90 555 123 4567',
            hourly_rate=Decimal('500.00'),
            approval_status='approved'
        )

    def test_consultation_booking_creation(self):
        """ConsultationBooking oluşturma testi"""
        from decimal import Decimal
        from datetime import date, time
        booking = ConsultationBooking.objects.create(
            client=self.client_user,
            consultant=self.consultant,
            booking_number='BOOK-001',
            scheduled_date=date.today(),
            scheduled_time=time(14, 0),
            duration_minutes=60,
            subject='Test Randevu',
            description='Test açıklama',
            quoted_price=Decimal('500.00'),
            meeting_type='online'
        )
        self.assertEqual(booking.client, self.client_user)
        self.assertEqual(booking.consultant, self.consultant)
        self.assertEqual(booking.status, 'pending')

    def test_consultation_booking_calculate_commission(self):
        """ConsultationBooking komisyon hesaplama testi"""
        from decimal import Decimal
        from datetime import date, time
        booking = ConsultationBooking.objects.create(
            client=self.client_user,
            consultant=self.consultant,
            booking_number='BOOK-002',
            scheduled_date=date.today(),
            scheduled_time=time(14, 0),
            duration_minutes=60,
            subject='Test Randevu',
            description='Test açıklama',
            quoted_price=Decimal('1000.00'),
            meeting_type='online'
        )
        booking.calculate_commission()
        # %15 komisyon
        self.assertEqual(booking.commission_amount, Decimal('150.00'))
        self.assertEqual(booking.consultant_earning, Decimal('850.00'))

