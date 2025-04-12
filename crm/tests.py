from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from unittest.mock import patch, MagicMock

from .models import Customer, Opportunity, Activity, Sale, Report
from .services import CustomerAnalyticsService, ReportGenerationService, EDocumentService, AccountingIntegrationService

User = get_user_model()

class CustomerModelTest(TestCase):
    """Müşteri modeli testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.customer = Customer.objects.create(
            name='Test Şirketi',
            contact_person='Ahmet Yılmaz',
            email='info@testfirma.com',
            phone='5321234567',
            address='Test Caddesi, No:123, Ankara',
            customer_type='corporate',
            created_by=self.user
        )
    
    def test_customer_creation(self):
        """Müşteri oluşturma testi"""
        self.assertEqual(self.customer.name, 'Test Şirketi')
        self.assertEqual(self.customer.contact_person, 'Ahmet Yılmaz')
        self.assertEqual(self.customer.email, 'info@testfirma.com')
        self.assertEqual(self.customer.phone, '5321234567')
        self.assertEqual(self.customer.customer_type, 'corporate')
        self.assertEqual(self.customer.created_by, self.user)
    
    def test_customer_str(self):
        """Müşteri __str__ metodu testi"""
        self.assertEqual(str(self.customer), 'Test Şirketi')

class OpportunityModelTest(TestCase):
    """Fırsat modeli testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.customer = Customer.objects.create(
            name='Test Şirketi',
            contact_person='Ahmet Yılmaz',
            email='info@testfirma.com',
            phone='5321234567',
            customer_type='corporate',
            created_by=self.user
        )
        self.opportunity = Opportunity.objects.create(
            customer=self.customer,
            title='Yeni Satış Fırsatı',
            description='Test açıklaması',
            value=Decimal('15000.00'),
            status='open',
            expected_close_date=timezone.now() + timedelta(days=30),
            created_by=self.user
        )
    
    def test_opportunity_creation(self):
        """Fırsat oluşturma testi"""
        self.assertEqual(self.opportunity.customer, self.customer)
        self.assertEqual(self.opportunity.title, 'Yeni Satış Fırsatı')
        self.assertEqual(self.opportunity.description, 'Test açıklaması')
        self.assertEqual(self.opportunity.value, Decimal('15000.00'))
        self.assertEqual(self.opportunity.status, 'open')
        self.assertEqual(self.opportunity.created_by, self.user)
    
    def test_opportunity_str(self):
        """Fırsat __str__ metodu testi"""
        self.assertEqual(str(self.opportunity), 'Yeni Satış Fırsatı - Test Şirketi')

class ActivityModelTest(TestCase):
    """Aktivite modeli testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.customer = Customer.objects.create(
            name='Test Şirketi',
            contact_person='Ahmet Yılmaz',
            email='info@testfirma.com',
            phone='5321234567',
            customer_type='corporate',
            created_by=self.user
        )
        self.activity = Activity.objects.create(
            customer=self.customer,
            activity_type='call',
            subject='Tanıtım Görüşmesi',
            description='Ürün tanıtımı yapıldı',
            date=timezone.now(),
            created_by=self.user
        )
    
    def test_activity_creation(self):
        """Aktivite oluşturma testi"""
        self.assertEqual(self.activity.customer, self.customer)
        self.assertEqual(self.activity.activity_type, 'call')
        self.assertEqual(self.activity.subject, 'Tanıtım Görüşmesi')
        self.assertEqual(self.activity.description, 'Ürün tanıtımı yapıldı')
        self.assertEqual(self.activity.created_by, self.user)
    
    def test_activity_str(self):
        """Aktivite __str__ metodu testi"""
        self.assertEqual(str(self.activity), 'Tanıtım Görüşmesi - Test Şirketi')

class CustomerAnalyticsServiceTest(TestCase):
    """Müşteri analiz servisi testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Müşteriler oluştur
        self.customer1 = Customer.objects.create(
            name='Şirket A',
            customer_type='corporate',
            created_by=self.user
        )
        
        self.customer2 = Customer.objects.create(
            name='Şirket B',
            customer_type='corporate',
            created_by=self.user
        )
        
        # Satışlar oluştur
        self.sale1 = Sale.objects.create(
            customer=self.customer1,
            product='Ürün A',
            amount=Decimal('5000.00'),
            date=timezone.now() - timedelta(days=10),
            created_by=self.user
        )
        
        self.sale2 = Sale.objects.create(
            customer=self.customer1,
            product='Ürün B',
            amount=Decimal('3000.00'),
            date=timezone.now() - timedelta(days=5),
            created_by=self.user
        )
        
        self.sale3 = Sale.objects.create(
            customer=self.customer2,
            product='Ürün A',
            amount=Decimal('2000.00'),
            date=timezone.now() - timedelta(days=7),
            created_by=self.user
        )
        
        # Analiz servisi oluştur
        self.analytics_service = CustomerAnalyticsService()
    
    def test_top_customers_by_revenue(self):
        """En çok gelir getiren müşteriler testi"""
        top_customers = self.analytics_service.get_top_customers_by_revenue(limit=2)
        
        self.assertEqual(len(top_customers), 2)
        self.assertEqual(top_customers[0]['customer'], self.customer1)
        self.assertEqual(top_customers[0]['total_revenue'], Decimal('8000.00'))
        self.assertEqual(top_customers[1]['customer'], self.customer2)
        self.assertEqual(top_customers[1]['total_revenue'], Decimal('2000.00'))
    
    def test_sales_by_period(self):
        """Dönemsel satış analizi testi"""
        start_date = timezone.now() - timedelta(days=15)
        end_date = timezone.now()
        
        sales_data = self.analytics_service.get_sales_by_period(start_date, end_date)
        
        self.assertEqual(sales_data['total_sales'], Decimal('10000.00'))
        self.assertEqual(sales_data['sale_count'], 3)
        self.assertEqual(sales_data['avg_sale_value'], Decimal('3333.33'))
    
    def test_customer_segmentation(self):
        """Müşteri segmentasyonu testi"""
        segments = self.analytics_service.segment_customers_by_value()
        
        self.assertTrue('high_value' in segments)
        self.assertTrue('medium_value' in segments)
        self.assertTrue('low_value' in segments)
        
        # Şirket A yüksek değerli segmentte olmalı
        self.assertIn(self.customer1, segments['high_value'])

class ReportGenerationServiceTest(TestCase):
    """Rapor oluşturma servisi testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.customer = Customer.objects.create(
            name='Test Şirketi',
            contact_person='Ahmet Yılmaz',
            customer_type='corporate',
            created_by=self.user
        )
        
        # Satışlar oluştur
        for i in range(5):
            Sale.objects.create(
                customer=self.customer,
                product=f'Ürün {i+1}',
                amount=Decimal(f'{(i+1)*1000}.00'),
                date=timezone.now() - timedelta(days=i*3),
                created_by=self.user
            )
        
        # Fırsatlar oluştur
        for i in range(3):
            Opportunity.objects.create(
                customer=self.customer,
                title=f'Fırsat {i+1}',
                value=Decimal(f'{(i+1)*2000}.00'),
                status='open',
                expected_close_date=timezone.now() + timedelta(days=(i+1)*10),
                created_by=self.user
            )
        
        # Aktiviteler oluştur
        for i in range(4):
            Activity.objects.create(
                customer=self.customer,
                activity_type='call' if i % 2 == 0 else 'meeting',
                subject=f'Aktivite {i+1}',
                date=timezone.now() - timedelta(days=i*2),
                created_by=self.user
            )
        
        self.report_service = ReportGenerationService()
    
    def test_generate_sales_report(self):
        """Satış raporu oluşturma testi"""
        start_date = timezone.now() - timedelta(days=20)
        end_date = timezone.now()
        
        report = self.report_service.generate_sales_report(
            name="Test Satış Raporu",
            description="Test açıklaması",
            start_date=start_date,
            end_date=end_date,
            created_by=self.user
        )
        
        self.assertEqual(report.name, "Test Satış Raporu")
        self.assertEqual(report.type, "sales")
        self.assertEqual(report.created_by, self.user)
        
        # Satış verilerini kontrol et
        sales_data = report.get_data()
        self.assertEqual(sales_data['total_sales'], Decimal('15000.00'))
        self.assertEqual(sales_data['sales_count'], 5)
    
    def test_generate_customer_activity_report(self):
        """Müşteri aktivite raporu oluşturma testi"""
        report = self.report_service.generate_customer_activity_report(
            customer=self.customer,
            name="Müşteri Aktivite Raporu",
            description="Son aktiviteler",
            created_by=self.user
        )
        
        self.assertEqual(report.name, "Müşteri Aktivite Raporu")
        self.assertEqual(report.type, "activity")
        
        # Aktivite verilerini kontrol et
        activity_data = report.get_data()
        self.assertEqual(activity_data['activity_count'], 4)
        self.assertEqual(activity_data['call_count'], 2)
        self.assertEqual(activity_data['meeting_count'], 2)
    
    def test_generate_opportunity_forecast_report(self):
        """Fırsat tahmin raporu oluşturma testi"""
        report = self.report_service.generate_opportunity_forecast_report(
            name="Fırsat Tahmin Raporu",
            description="Gelecek 60 gün için tahminler",
            forecast_period=60,
            created_by=self.user
        )
        
        self.assertEqual(report.name, "Fırsat Tahmin Raporu")
        self.assertEqual(report.type, "opportunity")
        
        # Fırsat verilerini kontrol et
        forecast_data = report.get_data()
        self.assertEqual(forecast_data['total_opportunity_value'], Decimal('12000.00'))
        self.assertEqual(forecast_data['opportunity_count'], 3)

class ReportViewsTest(TestCase):
    """Rapor görünümleri testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.client.login(username='testuser', password='testpassword')
        
        self.report = Report.objects.create(
            name="Test Raporu",
            description="Test açıklaması",
            type="sales",
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now(),
            created_by=self.user
        )
    
    def test_report_list_view(self):
        """Rapor listesi görünümü testi"""
        url = reverse('crm:report_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/report_list.html')
        self.assertContains(response, "Test Raporu")
    
    def test_report_detail_view(self):
        """Rapor detayı görünümü testi"""
        url = reverse('crm:report_detail', kwargs={'pk': self.report.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/report_detail.html')
        self.assertContains(response, "Test Raporu")
    
    def test_report_create_view(self):
        """Rapor oluşturma görünümü testi"""
        url = reverse('crm:report_create')
        
        # GET isteği
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/report_form.html')
        
        # POST isteği
        data = {
            'name': 'Yeni Rapor',
            'description': 'Açıklama',
            'type': 'customer',
            'start_date': timezone.now() - timedelta(days=30),
            'end_date': timezone.now(),
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Yönlendirme
        
        # Yeni raporun oluşturulduğunu kontrol et
        self.assertTrue(Report.objects.filter(name='Yeni Rapor').exists())
    
    def test_report_delete_view(self):
        """Rapor silme görünümü testi"""
        url = reverse('crm:report_delete', kwargs={'pk': self.report.pk})
        
        # GET isteği
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'crm/report_confirm_delete.html')
        
        # POST isteği
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Yönlendirme
        
        # Raporun silindiğini kontrol et
        self.assertFalse(Report.objects.filter(pk=self.report.pk).exists())

class EDocumentServiceTest(TestCase):
    """E-belge entegrasyon servisi testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.customer = Customer.objects.create(
            name='E-Belge Test Şirketi',
            contact_person='Ahmet Yılmaz',
            email='info@testfirma.com',
            phone='5321234567',
            tax_number='1234567890',
            tax_office='Ankara VD',
            address='Test Caddesi, No:123, Ankara',
            customer_type='corporate',
            created_by=self.user
        )
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            product='Test Ürünü',
            amount=Decimal('1180.00'),
            date=timezone.now(),
            notes='Test satışı',
            created_by=self.user
        )
        
        # Settings patch ile EDocumentService için gerekli ayarları yapılandır
        self.settings_patcher = patch('django.conf.settings')
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.EDOCUMENT_API_URL = 'https://api.example.com'
        self.mock_settings.EDOCUMENT_API_KEY = 'test_api_key'
        
        self.e_document_service = EDocumentService()
    
    def tearDown(self):
        self.settings_patcher.stop()
    
    def test_init_with_missing_settings(self):
        """Eksik ayarlarla başlatma durumunu test eder"""
        self.mock_settings.EDOCUMENT_API_URL = None
        
        with self.assertRaises(ValueError):
            EDocumentService()
    
    @patch('requests.get')
    def test_check_customer_e_invoice_status_success(self, mock_get):
        """Müşteri e-fatura durumu kontrolünü test eder (başarılı durum)"""
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'isEInvoiceRegistered': True,
            'isEArchiveRegistered': True,
            'title': 'E-Belge Test Şirketi',
            'taxOffice': 'Ankara VD'
        }
        mock_get.return_value = mock_response
        
        # Servisi çağır
        result = self.e_document_service.check_customer_e_invoice_status('1234567890')
        
        # Sonuçları kontrol et
        self.assertTrue(result['status'])
        self.assertTrue(result['is_e_invoice_registered'])
        self.assertTrue(result['is_e_archive_registered'])
        self.assertEqual(result['title'], 'E-Belge Test Şirketi')
        
        # API çağrısının doğru parametrelerle yapıldığını kontrol et
        mock_get.assert_called_once_with(
            'https://api.example.com/taxpayers/1234567890',
            headers=self.e_document_service.get_headers()
        )
    
    @patch('requests.get')
    def test_check_customer_e_invoice_status_error(self, mock_get):
        """Müşteri e-fatura durumu kontrolünü test eder (hata durumu)"""
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not Found'
        mock_get.return_value = mock_response
        
        # Servisi çağır
        result = self.e_document_service.check_customer_e_invoice_status('1234567890')
        
        # Sonuçları kontrol et
        self.assertFalse(result['status'])
        self.assertIn('API hatası', result['message'])
    
    @patch('requests.post')
    def test_create_invoice_from_sale_success(self, mock_post):
        """Satıştan e-fatura oluşturmayı test eder (başarılı durum)"""
        # Mock response hazırla
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 123,
            'uuid': 'test-uuid-123',
            'number': 'INV-2023-001'
        }
        mock_post.return_value = mock_response
        
        # Servisi çağır
        result = self.e_document_service.create_invoice_from_sale(self.sale, e_invoice=True)
        
        # Sonuçları kontrol et
        self.assertTrue(result['status'])
        self.assertEqual(result['invoice_id'], 123)
        self.assertEqual(result['uuid'], 'test-uuid-123')
        self.assertEqual(result['number'], 'INV-2023-001')
        
        # API çağrısının doğru parametrelerle yapıldığını kontrol et
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('/e-invoices', call_args[0][0])
        
        # Gönderilen verileri kontrol et
        json_data = call_args[1]['json']
        self.assertEqual(json_data['customer']['identifier'], '1234567890')
        self.assertEqual(json_data['customer']['name'], 'E-Belge Test Şirketi')
        self.assertEqual(float(json_data['totalAmount']), 1180.0)
    
    @patch('requests.post')
    def test_create_invoice_missing_tax_number(self, mock_post):
        """Vergi numarası olmadan e-fatura oluşturmayı test eder"""
        # Vergi numarası olmayan müşteri oluştur
        customer_without_tax = Customer.objects.create(
            name='Vergi Numarası Olmayan Şirket',
            customer_type='corporate',
            created_by=self.user
        )
        
        sale = Sale.objects.create(
            customer=customer_without_tax,
            product='Test Ürünü',
            amount=Decimal('1000.00'),
            date=timezone.now(),
            created_by=self.user
        )
        
        # Servisi çağır
        result = self.e_document_service.create_invoice_from_sale(sale, e_invoice=True)
        
        # Sonuçları kontrol et
        self.assertFalse(result['status'])
        self.assertEqual(result['message'], 'Müşterinin vergi numarası bulunamadı')
        
        # API'ye hiç çağrı yapılmadığını kontrol et
        mock_post.assert_not_called()

class AccountingIntegrationServiceTest(TestCase):
    """Muhasebe entegrasyon servisi testleri"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.customer = Customer.objects.create(
            name='Muhasebe Test Şirketi',
            contact_person='Mehmet Demir',
            email='info@muhasebetest.com',
            phone='5331234567',
            tax_number='9876543210',
            tax_office='İstanbul VD',
            address='Finans Caddesi, No:456, İstanbul',
            customer_type='corporate',
            created_by=self.user
        )
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            product='Muhasebe Yazılımı',
            amount=Decimal('2360.00'),
            date=timezone.now(),
            notes='Yıllık lisans',
            created_by=self.user
        )
        
        # Muhasebe modeline mock oluştur
        self.account_model_patcher = patch('accounting.models.Account')
        self.mock_account_model = self.account_model_patcher.start()
        
        self.transaction_model_patcher = patch('accounting.models.Transaction')
        self.mock_transaction_model = self.transaction_model_patcher.start()
        
        self.transaction_line_model_patcher = patch('accounting.models.TransactionLine')
        self.mock_transaction_line_model = self.transaction_line_model_patcher.start()
        
        self.django_transaction_patcher = patch('django.db.transaction')
        self.mock_django_transaction = self.django_transaction_patcher.start()
        
        self.accounting_service = AccountingIntegrationService()
    
    def tearDown(self):
        self.account_model_patcher.stop()
        self.transaction_model_patcher.stop()
        self.transaction_line_model_patcher.stop()
        self.django_transaction_patcher.stop()
    
    def test_create_accounting_record_from_sale_new_account(self):
        """Yeni cari hesap oluşturarak muhasebe kaydı oluşturmayı test eder"""
        # Mock account objesi yok (yeni oluşturulacak)
        self.mock_account_model.objects.filter().first.return_value = None
        
        # Mock transaction objesi
        mock_transaction = MagicMock()
        mock_transaction.id = 123
        mock_transaction.number = 'YEV-20230101123456'
        self.mock_transaction_model.objects.create.return_value = mock_transaction
        
        # Mock account objesi
        mock_account = MagicMock()
        self.mock_account_model.objects.create.return_value = mock_account
        
        # Servisi çağır
        result = self.accounting_service.create_accounting_record_from_sale(self.sale)
        
        # Sonuçları kontrol et
        self.assertTrue(result['status'])
        self.assertEqual(result['transaction_id'], 123)
        self.assertEqual(result['transaction_number'], 'YEV-20230101123456')
        
        # Muhasebe modellerine yapılan çağrıları kontrol et
        self.mock_account_model.objects.create.assert_called_once()
        self.mock_transaction_model.objects.create.assert_called_once()
        self.assertEqual(self.mock_transaction_line_model.objects.create.call_count, 3)  # 3 muhasebe kaydı
        
        # Cari hesap bakiyesinin güncellendiğini kontrol et
        mock_account.save.assert_called_once()
    
    def test_create_accounting_record_from_sale_existing_account(self):
        """Mevcut cari hesap ile muhasebe kaydı oluşturmayı test eder"""
        # Mock mevcut account objesi
        mock_existing_account = MagicMock()
        mock_existing_account.balance = Decimal('0')
        self.mock_account_model.objects.filter().first.return_value = mock_existing_account
        
        # Mock transaction objesi
        mock_transaction = MagicMock()
        mock_transaction.id = 456
        mock_transaction.number = 'YEV-20230101654321'
        self.mock_transaction_model.objects.create.return_value = mock_transaction
        
        # Servisi çağır
        result = self.accounting_service.create_accounting_record_from_sale(self.sale)
        
        # Sonuçları kontrol et
        self.assertTrue(result['status'])
        self.assertEqual(result['transaction_id'], 456)
        
        # Muhasebe modellerine yapılan çağrıları kontrol et
        self.mock_account_model.objects.create.assert_not_called()  # Mevcut hesap olduğu için oluşturma yapılmaz
        self.mock_transaction_model.objects.create.assert_called_once()
        
        # Cari hesap bakiyesinin güncellendiğini kontrol et
        self.assertEqual(mock_existing_account.balance, Decimal('2360.00'))
        mock_existing_account.save.assert_called_once()
    
    @patch('django.db.transaction.atomic')
    def test_create_accounting_record_exception(self, mock_atomic):
        """Hata durumunda muhasebe kaydı oluşturmayı test eder"""
        # atomic işleminde hata fırlat
        mock_atomic.side_effect = Exception('Test hata')
        
        # Servisi çağır
        result = self.accounting_service.create_accounting_record_from_sale(self.sale)
        
        # Sonuçları kontrol et
        self.assertFalse(result['status'])
        self.assertIn('Muhasebe kaydı oluşturulamadı', result['message'])
    
    def test_sync_customer_with_account_update(self):
        """Müşteri bilgilerini mevcut cari hesaba senkronize etmeyi test eder"""
        # Mock mevcut account objesi
        mock_existing_account = MagicMock()
        mock_existing_account.id = 789
        self.mock_account_model.objects.filter().first.return_value = mock_existing_account
        
        # Servisi çağır
        result = self.accounting_service.sync_customer_with_account(self.customer)
        
        # Sonuçları kontrol et
        self.assertTrue(result['status'])
        self.assertEqual(result['message'], 'Cari hesap güncellendi')
        self.assertEqual(result['account_id'], 789)
        
        # Hesap bilgilerinin güncellendiğini kontrol et
        self.assertEqual(mock_existing_account.tax_number, '9876543210')
        self.assertEqual(mock_existing_account.tax_office, 'İstanbul VD')
        self.assertEqual(mock_existing_account.address, 'Finans Caddesi, No:456, İstanbul')
        self.assertEqual(mock_existing_account.phone, '5331234567')
        self.assertEqual(mock_existing_account.email, 'info@muhasebetest.com')
        mock_existing_account.save.assert_called_once()
    
    def test_sync_customer_with_account_create(self):
        """Müşteri için yeni cari hesap oluşturmayı test eder"""
        # Mevcut hesap yok
        self.mock_account_model.objects.filter().first.return_value = None
        
        # Mock yeni account objesi
        mock_new_account = MagicMock()
        mock_new_account.id = 999
        self.mock_account_model.objects.create.return_value = mock_new_account
        
        # Servisi çağır
        result = self.accounting_service.sync_customer_with_account(self.customer)
        
        # Sonuçları kontrol et
        self.assertTrue(result['status'])
        self.assertEqual(result['message'], 'Yeni cari hesap oluşturuldu')
        self.assertEqual(result['account_id'], 999)
        
        # Yeni hesabın oluşturulduğunu kontrol et
        create_call_kwargs = self.mock_account_model.objects.create.call_args[1]
        self.assertEqual(create_call_kwargs['name'], 'Muhasebe Test Şirketi')
        self.assertEqual(create_call_kwargs['tax_number'], '9876543210')
        self.assertEqual(create_call_kwargs['type'], 'customer')
