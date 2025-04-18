from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from decimal import Decimal
import requests
from datetime import date, datetime, timedelta
from django.conf import settings
import logging
from django.db import transaction
from django.core.files.base import ContentFile

from .models import Customer, Opportunity, Activity, Sale, Document, Campaign, CampaignUsage, ReferralProgram, PremiumPackage, ConsultingService, TrainingProgram, APIPricing, ServiceSubscription, LoyaltyProgram, LoyaltyLevel, CustomerLoyalty, SeasonalCampaign, PartnershipProgram, Partner
from apps.accounting.models import Account, Invoice, InvoiceLine

logger = logging.getLogger(__name__)


class CustomerAnalyticsService:
    """Müşteri veri analizi servisi"""
    
    def __init__(self):
        self.segment_thresholds = {
            'high_value': Decimal('10000.00'),
            'medium_value': Decimal('5000.00'),
            'low_value': Decimal('1000.00')
        }
    
    def get_top_customers_by_revenue(self, limit=5, start_date=None, end_date=None):
        """En çok gelir getiren müşterileri döndürür"""
        sales_query = Sale.objects.all()
        
        if start_date and end_date:
            sales_query = sales_query.filter(date__range=[start_date, end_date])
        
        customers = Customer.objects.annotate(
            total_revenue=Sum('sales__amount')
        ).filter(total_revenue__gt=0).order_by('-total_revenue')[:limit]
        
        return [
            {
                'customer': customer,
                'total_revenue': customer.total_revenue
            }
            for customer in customers
        ]
    
    def get_sales_by_period(self, start_date, end_date):
        """Belirli bir dönem için satış analizini döndürür"""
        sales = Sale.objects.filter(date__range=[start_date, end_date])
        
        total_sales = sales.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        sale_count = sales.count()
        avg_sale_value = Decimal('0')
        
        if sale_count > 0:
            avg_sale_value = (total_sales / sale_count).quantize(Decimal('0.01'))
        
        return {
            'total_sales': total_sales,
            'sale_count': sale_count,
            'avg_sale_value': avg_sale_value,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def segment_customers_by_value(self):
        """Müşterileri değerlerine göre segmentlere ayırır"""
        # Segmentleri değer aralıklarına göre tanımla
        high_threshold = Decimal('5000.00')
        medium_threshold = Decimal('1000.00')
        
        # Tüm müşterileri değerlerine göre sırala
        customers_with_value = Customer.objects.annotate(
            total_revenue=Sum('sales__amount', default=0)
        )
        
        # Segmentlere ayır
        high_value = customers_with_value.filter(total_revenue__gte=high_threshold)
        medium_value = customers_with_value.filter(
            total_revenue__lt=high_threshold, 
            total_revenue__gte=medium_threshold
        )
        low_value = customers_with_value.filter(
            total_revenue__lt=medium_threshold
        )
        
        return {
            'high_value': high_value,
            'medium_value': medium_value,
            'low_value': low_value
        }
    
    def get_customer_activity_metrics(self, customer, days=30):
        """Müşteri aktivite metriklerini döndürür"""
        start_date = timezone.now() - timedelta(days=days)
        activities = Activity.objects.filter(
            customer=customer,
            date__gte=start_date
        )
        
        return {
            'total_activities': activities.count(),
            'calls': activities.filter(activity_type='call').count(),
            'meetings': activities.filter(activity_type='meeting').count(),
            'emails': activities.filter(activity_type='email').count(),
            'tasks': activities.filter(activity_type='task').count(),
            'last_activity_date': activities.order_by('-date').first().date if activities.exists() else None
        }
    
    def get_detailed_customer_segments(self):
        """Detaylı müşteri segmentasyonu yapar"""
        segments = {
            'value_based': self._segment_by_value(),
            'behavior_based': self._segment_by_behavior(),
            'demographic': self._segment_by_demographics(),
            'engagement': self._segment_by_engagement()
        }
        return segments
    
    def _segment_by_value(self):
        """Değer bazlı segmentasyon"""
        return {
            'high_value': Customer.objects.filter(total_revenue__gte=self.segment_thresholds['high_value']),
            'medium_value': Customer.objects.filter(
                total_revenue__lt=self.segment_thresholds['high_value'],
                total_revenue__gte=self.segment_thresholds['medium_value']
            ),
            'low_value': Customer.objects.filter(
                total_revenue__lt=self.segment_thresholds['medium_value'],
                total_revenue__gte=self.segment_thresholds['low_value']
            ),
            'minimal_value': Customer.objects.filter(total_revenue__lt=self.segment_thresholds['low_value'])
        }
    
    def _segment_by_behavior(self):
        """Davranış bazlı segmentasyon"""
        return {
            'frequent_buyers': Customer.objects.filter(purchase_frequency__gte=5),
            'seasonal_buyers': Customer.objects.filter(is_seasonal=True),
            'loyal_customers': Customer.objects.filter(loyalty_score__gte=8),
            'at_risk': Customer.objects.filter(last_purchase_date__lt=timezone.now() - timedelta(days=180))
        }
    
    def _segment_by_demographics(self):
        """Demografik segmentasyon"""
        return {
            'enterprise': Customer.objects.filter(customer_type='enterprise'),
            'sme': Customer.objects.filter(customer_type='sme'),
            'startup': Customer.objects.filter(customer_type='startup'),
            'individual': Customer.objects.filter(customer_type='individual')
        }
    
    def _segment_by_engagement(self):
        """Etkileşim bazlı segmentasyon"""
        return {
            'high_engagement': Customer.objects.filter(engagement_score__gte=8),
            'medium_engagement': Customer.objects.filter(
                engagement_score__lt=8,
                engagement_score__gte=5
            ),
            'low_engagement': Customer.objects.filter(engagement_score__lt=5)
        }
    
    def get_market_analysis(self):
        """Gelişmiş pazar analizi"""
        return {
            'market_size': self._calculate_market_size(),
            'growth_rate': self._calculate_market_growth(),
            'trends': self._analyze_market_trends(),
            'opportunities': self._identify_market_opportunities()
        }
    
    def _calculate_market_size(self):
        """Pazar büyüklüğü hesaplama"""
        total_revenue = Customer.objects.aggregate(
            total=Sum('total_revenue')
        )['total'] or Decimal('0')
        
        market_share = Decimal('0.15')  # Örnek pazar payı
        return total_revenue / market_share
    
    def _calculate_market_growth(self):
        """Pazar büyüme oranı hesaplama"""
        current_year = timezone.now().year
        last_year = current_year - 1
        
        current_revenue = Customer.objects.filter(
            created_at__year=current_year
        ).aggregate(total=Sum('total_revenue'))['total'] or Decimal('0')
        
        last_year_revenue = Customer.objects.filter(
            created_at__year=last_year
        ).aggregate(total=Sum('total_revenue'))['total'] or Decimal('0')
        
        if last_year_revenue == 0:
            return Decimal('0')
        
        return ((current_revenue - last_year_revenue) / last_year_revenue) * 100
    
    def _analyze_market_trends(self):
        """Pazar trendlerini analiz et"""
        trends = {
            'seasonal_patterns': self._analyze_seasonality(),
            'product_preferences': self._analyze_product_preferences(),
            'price_sensitivity': self._analyze_price_sensitivity(),
            'technology_adoption': self._analyze_tech_adoption()
        }
        return trends
    
    def _identify_market_opportunities(self):
        """Pazar fırsatlarını belirle"""
        return {
            'untapped_segments': self._find_untapped_segments(),
            'growth_areas': self._identify_growth_areas(),
            'new_markets': self._identify_new_markets(),
            'product_gaps': self._identify_product_gaps()
        }
    
    def get_competitor_analysis(self):
        """Rakip analizi"""
        return {
            'market_share': self._analyze_market_share(),
            'competitive_advantages': self._analyze_competitive_advantages(),
            'pricing_strategy': self._analyze_pricing_strategy(),
            'customer_satisfaction': self._analyze_customer_satisfaction()
        }
    
    def _analyze_market_share(self):
        """Pazar payı analizi"""
        total_market = self._calculate_market_size()
        our_revenue = Customer.objects.aggregate(
            total=Sum('total_revenue')
        )['total'] or Decimal('0')
        
        return {
            'our_share': (our_revenue / total_market) * 100,
            'competitor_shares': self._get_competitor_shares()
        }
    
    def get_predictive_analytics(self):
        """Tahminsel analitik özellikleri"""
        return {
            'customer_lifetime_value': self._predict_customer_lifetime_value(),
            'churn_probability': self._predict_churn_probability(),
            'next_best_offer': self._predict_next_best_offer(),
            'revenue_forecast': self._forecast_revenue()
        }
    
    def _predict_customer_lifetime_value(self):
        """Müşteri yaşam boyu değeri tahmini"""
        customers = Customer.objects.all()
        predictions = {}
        
        for customer in customers:
            avg_purchase = customer.total_revenue / max(customer.purchase_count, 1)
            purchase_frequency = customer.purchase_frequency
            customer_lifespan = 5  # Yıl cinsinden ortalama müşteri ömrü
            
            clv = avg_purchase * purchase_frequency * customer_lifespan
            predictions[customer.id] = clv
        
        return predictions
    
    def _predict_churn_probability(self):
        """Müşteri kaybı olasılığı tahmini"""
        customers = Customer.objects.all()
        predictions = {}
        
        for customer in customers:
            # Churn skorunu hesapla
            recency = (timezone.now() - customer.last_purchase_date).days
            frequency = customer.purchase_frequency
            monetary = customer.total_revenue
            
            # RFM skoruna dayalı basit bir churn tahmini
            churn_prob = min(1.0, (recency / 365) * (1 - frequency/10) * (1 - monetary/10000))
            predictions[customer.id] = churn_prob
        
        return predictions
    
    def _predict_next_best_offer(self):
        """Sonraki en iyi teklif tahmini"""
        customers = Customer.objects.all()
        predictions = {}
        
        for customer in customers:
            # Müşterinin geçmiş davranışlarına dayalı öneriler
            preferences = self._analyze_customer_preferences(customer)
            predictions[customer.id] = preferences
        
        return predictions
    
    def _forecast_revenue(self):
        """Gelir tahmini"""
        # Son 12 ayın verilerini kullan
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        historical_data = Customer.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('created_at__month').annotate(
            revenue=Sum('total_revenue')
        ).order_by('created_at__month')
        
        # Basit bir doğrusal regresyon tahmini
        forecast = self._linear_regression_forecast(historical_data)
        return forecast


class ReportGenerationService:
    """Rapor oluşturma servisi"""
    
    def generate_sales_report(self, name, description, start_date, end_date, created_by):
        """Satış raporu oluşturur"""
        report = Report.objects.create(
            name=name,
            description=description,
            type="sales",
            start_date=start_date,
            end_date=end_date,
            created_by=created_by
        )
        
        # Rapor verilerini hesapla
        sales = Sale.objects.filter(date__range=[start_date, end_date])
        
        # Metadata olarak kaydedilecek verileri hesapla
        metadata = {
            'total_sales': str(sales.aggregate(total=Sum('amount'))['total'] or 0),
            'sales_count': sales.count(),
            'top_products': list(sales.values('product').annotate(
                count=Count('id'),
                total=Sum('amount')
            ).order_by('-total')[:5])
        }
        
        # Rapor metadatasını güncelle
        report.metadata = metadata
        report.save()
        
        return report
    
    def generate_customer_activity_report(self, customer, name, description, created_by):
        """Müşteri aktivite raporu oluşturur"""
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        
        report = Report.objects.create(
            name=name,
            description=description,
            type="activity",
            start_date=start_date,
            end_date=today,
            customer=customer,
            created_by=created_by
        )
        
        # Aktivite verilerini hesapla
        activities = Activity.objects.filter(
            customer=customer,
            date__range=[start_date, today]
        )
        
        # Metadata olarak kaydedilecek verileri hesapla
        metadata = {
            'activity_count': activities.count(),
            'call_count': activities.filter(activity_type='call').count(),
            'meeting_count': activities.filter(activity_type='meeting').count(),
            'email_count': activities.filter(activity_type='email').count(),
            'task_count': activities.filter(activity_type='task').count(),
        }
        
        # Rapor metadatasını güncelle
        report.metadata = metadata
        report.save()
        
        return report
    
    def generate_opportunity_forecast_report(self, name, description, forecast_period, created_by):
        """Fırsat tahmin raporu oluşturur"""
        today = timezone.now().date()
        end_date = today + timedelta(days=forecast_period)
        
        report = Report.objects.create(
            name=name,
            description=description,
            type="opportunity",
            start_date=today,
            end_date=end_date,
            created_by=created_by
        )
        
        # Fırsat verilerini hesapla
        opportunities = Opportunity.objects.filter(
            expected_close_date__range=[today, end_date],
            status__in=['new', 'qualified', 'proposal', 'negotiation']
        )
        
        # Metadata olarak kaydedilecek verileri hesapla
        metadata = {
            'opportunity_count': opportunities.count(),
            'total_opportunity_value': str(opportunities.aggregate(total=Sum('value'))['total'] or 0),
            'by_stage': {
                'new': str(opportunities.filter(status='new').aggregate(total=Sum('value'))['total'] or 0),
                'qualified': str(opportunities.filter(status='qualified').aggregate(total=Sum('value'))['total'] or 0),
                'proposal': str(opportunities.filter(status='proposal').aggregate(total=Sum('value'))['total'] or 0),
                'negotiation': str(opportunities.filter(status='negotiation').aggregate(total=Sum('value'))['total'] or 0),
            }
        }
        
        # Rapor metadatasını güncelle
        report.metadata = metadata
        report.save()
        
        return report


class EDocumentService:
    """E-belge entegrasyonu için servis sınıfı"""
    
    def __init__(self, api_url=None, api_key=None):
        self.api_url = api_url or getattr(settings, 'EDOCUMENT_API_URL', None)
        self.api_key = api_key or getattr(settings, 'EDOCUMENT_API_KEY', None)
        
        if not self.api_url or not self.api_key:
            logger.warning("E-belge API yapılandırması eksik. EDOCUMENT_API_URL ve EDOCUMENT_API_KEY ayarları kontrol edilmeli.")
    
    def _make_request(self, endpoint, method='GET', data=None):
        """API isteği gönderir ve yanıtı döndürür"""
        if not self.api_url or not self.api_key:
            raise ValueError("E-belge API yapılandırması eksik")
        
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f'ApiKey {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data or {})
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data or {})
            else:
                raise ValueError(f"Desteklenmeyen HTTP metodu: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"E-belge API hatası: {str(e)}")
            raise
    
    def check_customer_e_invoice_status(self, customer):
        """Müşterinin e-fatura kullanıcısı olup olmadığını kontrol eder"""
        if not customer.tax_number:
            logger.warning(f"Müşteri {customer.name} için vergi numarası bulunamadı")
            return False
        
        # Son kontrolden bu yana 7 günden az süre geçmişse, tekrar kontrol etme
        if customer.e_invoice_last_check and customer.e_invoice_last_check > timezone.now() - timedelta(days=7):
            return customer.is_e_invoice_user
        
        try:
            data = {'tax_number': customer.tax_number}
            response = self._make_request('/api/check-e-invoice-user', 'POST', data)
            
            is_e_invoice_user = response.get('is_e_invoice_user', False)
            
            # Müşteri bilgilerini güncelle
            customer.is_e_invoice_user = is_e_invoice_user
            customer.e_invoice_last_check = timezone.now()
            customer.save(update_fields=['is_e_invoice_user', 'e_invoice_last_check'])
            
            return is_e_invoice_user
        except Exception as e:
            logger.error(f"Müşteri e-fatura durumu kontrolü başarısız oldu - {customer.name}: {str(e)}")
            return customer.is_e_invoice_user  # Hata durumunda mevcut değeri kullan
    
    def create_invoice_from_sale(self, sale):
        """Satış kaydından e-fatura veya e-arşiv fatura oluşturur"""
        if not sale or not sale.customer:
            raise ValueError("Geçerli bir satış ve müşteri gereklidir")
        
        # Müşteri e-fatura kullanıcısı mı kontrol et
        is_e_invoice = self.check_customer_e_invoice_status(sale.customer)
        invoice_type = 'e_invoice' if is_e_invoice else 'e_archive'
        
        # Fatura bilgileri hazırla
        invoice_data = {
            'type': invoice_type,
            'issue_date': timezone.now().strftime('%Y-%m-%d'),
            'customer': {
                'name': sale.customer.name,
                'tax_number': sale.customer.tax_number,
                'tax_office': sale.customer.tax_office,
                'address': sale.customer.address,
                'email': sale.customer.email,
                'phone': sale.customer.phone
            },
            'items': [
                {
                    'name': sale.product,
                    'quantity': 1,
                    'unit_price': float(sale.amount),
                    'total': float(sale.amount)
                }
            ],
            'notes': sale.notes
        }
        
        try:
            # E-belge API'sine istek gönder
            response = self._make_request('/api/create-invoice', 'POST', invoice_data)
            
            if not response.get('success'):
                raise ValueError(f"E-fatura oluşturma başarısız: {response.get('message', 'Bilinmeyen hata')}")
            
            # Satış kaydını güncelle
            with transaction.atomic():
                sale.invoice_status = 'invoiced'
                sale.invoice_number = response.get('invoice_number')
                sale.invoice_date = timezone.now()
                sale.invoice_type = invoice_type
                sale.save(update_fields=['invoice_status', 'invoice_number', 'invoice_date', 'invoice_type'])
                
                # Belge oluştur
                if response.get('pdf_url'):
                    pdf_response = requests.get(response.get('pdf_url'))
                    if pdf_response.status_code == 200:
                        document = Document(
                            title=f"Fatura {response.get('invoice_number')}",
                            document_type=invoice_type,
                            document_number=response.get('invoice_number'),
                            issue_date=timezone.now().date(),
                            customer=sale.customer,
                            sale=sale,
                            uuid=response.get('uuid'),
                            created_by=sale.created_by
                        )
                        document.file.save(
                            f"{invoice_type}_{response.get('invoice_number')}.pdf",
                            ContentFile(pdf_response.content),
                            save=False
                        )
                        document.save()
                
            return {
                'success': True,
                'invoice_number': response.get('invoice_number'),
                'invoice_type': invoice_type,
                'uuid': response.get('uuid')
            }
        except Exception as e:
            logger.error(f"E-fatura oluşturma başarısız - Satış ID {sale.id}: {str(e)}")
            raise


class AccountingIntegrationService:
    """Muhasebe entegrasyonu için servis sınıfı"""
    
    def __init__(self, client=None):
        self.client = client
    
    def get_or_create_customer_account(self, customer):
        """Müşteri için cari hesap oluşturur veya mevcut hesabı döndürür"""
        if customer.accounting_reference:
            try:
                account = Account.objects.get(code=customer.accounting_reference)
                return account
            except Account.DoesNotExist:
                pass
        
        # Hesap kodu oluştur
        code = f"120.{customer.id:05d}"
        
        # Hesap türü belirle
        account_type = 'customer'
        
        # Hesabı oluştur veya güncelle
        account, created = Account.objects.update_or_create(
            customer=customer,
            defaults={
                'name': customer.name,
                'code': code,
                'type': account_type,
                'notes': f"Müşteri ID: {customer.id}"
            }
        )
        
        # Müşteri referansını güncelle
        if created or not customer.accounting_reference:
            customer.accounting_reference = code
            customer.save(update_fields=['accounting_reference'])
        
        return account
    
    def create_accounting_record_from_sale(self, sale):
        """Satış kaydından muhasebe kaydı oluşturur"""
        if sale.accounting_status == 'processed' and sale.accounting_reference:
            return {'success': True, 'message': 'Bu satış zaten muhasebeleştirilmiş', 'reference': sale.accounting_reference}
        
        with transaction.atomic():
            try:
                # Müşteri hesabını al veya oluştur
                customer_account = self.get_or_create_customer_account(sale.customer)
                
                # Satış için fatura oluştur
                invoice = Invoice.objects.create(
                    customer=sale.customer,
                    account=customer_account,
                    invoice_no=sale.invoice_number or f"S{sale.id:06d}",
                    date=sale.invoice_date or sale.date,
                    due_date=(sale.invoice_date or sale.date) + timedelta(days=30),
                    total=sale.amount,
                    status='open',
                    notes=f"Otomatik oluşturuldu - Satış ID: {sale.id}"
                )
                
                # Fatura kalemi oluştur
                InvoiceLine.objects.create(
                    invoice=invoice,
                    description=sale.product,
                    quantity=1,
                    unit_price=sale.amount,
                    amount=sale.amount
                )
                
                # Satış kaydını güncelle
                sale.accounting_status = 'processed'
                sale.accounting_reference = f"INV-{invoice.id}"
                sale.save(update_fields=['accounting_status', 'accounting_reference'])
                
                return {
                    'success': True,
                    'message': 'Muhasebe kaydı başarıyla oluşturuldu',
                    'reference': sale.accounting_reference
                }
            except Exception as e:
                logger.error(f"Muhasebe kaydı oluşturma hatası - Satış ID {sale.id}: {str(e)}")
                sale.accounting_status = 'error'
                sale.save(update_fields=['accounting_status'])
                raise
    
    def sync_customer_with_account(self, customer):
        """Müşteri bilgilerini muhasebe sistemindeki cari hesapla senkronize eder"""
        with transaction.atomic():
            try:
                account = self.get_or_create_customer_account(customer)
                
                # Hesap bilgilerini güncelle
                account.name = customer.name
                account.save()
                
                return {
                    'success': True,
                    'message': 'Müşteri bilgileri muhasebe sistemiyle senkronize edildi',
                    'account_code': account.code
                }
            except Exception as e:
                logger.error(f"Müşteri senkronizasyonu hatası - Müşteri ID {customer.id}: {str(e)}")
                raise


class CustomerAcquisitionService:
    """Müşteri edinme stratejileri servisi"""
    
    def __init__(self):
        self.referral_bonus = Decimal('50.00')  # Referans başına bonus
        self.student_discount = Decimal('0.30')  # Öğrenci indirimi (%30)
        self.startup_discount = Decimal('0.20')  # Startup indirimi (%20)
        self.early_bird_discount = Decimal('0.15')  # Erken dönem indirimi (%15)
    
    def calculate_referral_reward(self, referred_customer_value: Decimal) -> Decimal:
        """Referans ödülünü hesaplar"""
        return self.referral_bonus + (referred_customer_value * Decimal('0.05'))
    
    def apply_student_discount(self, package_price: Decimal) -> Decimal:
        """Öğrenci indirimi uygular"""
        return package_price * (Decimal('1') - self.student_discount)
    
    def apply_startup_discount(self, package_price: Decimal) -> Decimal:
        """Startup indirimi uygular"""
        return package_price * (Decimal('1') - self.startup_discount)
    
    def apply_early_bird_discount(self, package_price: Decimal) -> Decimal:
        """Erken dönem indirimi uygular"""
        return package_price * (Decimal('1') - self.early_bird_discount)
    
    def get_trial_period_days(self, package_type: str) -> int:
        """Paket tipine göre deneme süresini döndürür"""
        trial_periods = {
            'kobi': 14,  # KOBİ paketi 14 gün
            'education': 30,  # Eğitim paketi 30 gün
            'corporate': 7  # Kurumsal paket 7 gün
        }
        return trial_periods.get(package_type, 7)
    
    def track_acquisition_channel(self, customer: Customer, channel: str):
        """Müşteri edinme kanalını kaydeder"""
        customer.acquisition_channel = channel
        customer.acquisition_date = timezone.now()
        customer.save()
        
        # Kanal bazlı analitik
        self._update_channel_analytics(channel)
    
    def _update_channel_analytics(self, channel: str):
        """Kanal bazlı analitikleri günceller"""
        try:
            analytics = CustomerAcquisitionAnalytics.objects.get(channel=channel)
            analytics.total_customers += 1
            analytics.last_updated = timezone.now()
            analytics.save()
        except CustomerAcquisitionAnalytics.DoesNotExist:
            CustomerAcquisitionAnalytics.objects.create(
                channel=channel,
                total_customers=1
            )
    
    def get_acquisition_metrics(self, start_date=None, end_date=None):
        """Müşteri edinme metriklerini döndürür"""
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
            
        customers = Customer.objects.filter(
            acquisition_date__range=[start_date, end_date]
        )
        
        total_customers = customers.count()
        channel_breakdown = customers.values('acquisition_channel').annotate(
            count=Count('id')
        )
        
        conversion_rate = self._calculate_conversion_rate(customers)
        acquisition_cost = self._calculate_acquisition_cost(customers)
        
        return {
            'total_customers': total_customers,
            'channel_breakdown': channel_breakdown,
            'conversion_rate': conversion_rate,
            'acquisition_cost': acquisition_cost,
            'period': {
                'start': start_date,
                'end': end_date
            }
        }
    
    def _calculate_conversion_rate(self, customers) -> float:
        """Dönüşüm oranını hesaplar"""
        total_trials = Customer.objects.filter(
            is_trial=True,
            acquisition_date__range=[
                customers.first().acquisition_date,
                customers.last().acquisition_date
            ]
        ).count()
        
        if total_trials == 0:
            return 0.0
            
        return (customers.count() / total_trials) * 100
    
    def _calculate_acquisition_cost(self, customers) -> Decimal:
        """Müşteri edinme maliyetini hesaplar"""
        total_cost = Decimal('0')
        
        # Kanal bazlı maliyetleri hesapla
        channel_costs = {
            'google_ads': Decimal('50.00'),
            'facebook_ads': Decimal('40.00'),
            'referral': Decimal('20.00'),
            'organic': Decimal('10.00')
        }
        
        for customer in customers:
            channel = customer.acquisition_channel
            if channel in channel_costs:
                total_cost += channel_costs[channel]
        
        return total_cost / customers.count() if customers.count() > 0 else Decimal('0')


class CampaignService:
    """Kampanya yönetimi servisi"""
    
    def __init__(self):
        self.student_discount = Decimal('30.00')  # %30 öğrenci indirimi
        self.startup_discount = Decimal('20.00')  # %20 startup indirimi
        self.referral_bonus = Decimal('50.00')    # ₺50 referans bonusu
    
    def create_student_campaign(self, start_date, end_date):
        """Öğrenci indirimi kampanyası oluşturur"""
        return Campaign.objects.create(
            name="Öğrenci İndirimi",
            campaign_type='student',
            description="Öğrencilere özel %30 indirim",
            discount_rate=self.student_discount,
            start_date=start_date,
            end_date=end_date
        )
    
    def create_startup_campaign(self, start_date, end_date):
        """Startup paketi kampanyası oluşturur"""
        return Campaign.objects.create(
            name="Startup Paketi",
            campaign_type='startup',
            description="Startup'lara özel %20 indirim",
            discount_rate=self.startup_discount,
            start_date=start_date,
            end_date=end_date
        )
    
    def create_referral_campaign(self, start_date, end_date):
        """Referans programı kampanyası oluşturur"""
        return Campaign.objects.create(
            name="Referans Programı",
            campaign_type='referral',
            description="Arkadaşını davet et, ₺50 bonus kazan",
            bonus_amount=self.referral_bonus,
            start_date=start_date,
            end_date=end_date
        )
    
    def apply_campaign(self, campaign, customer, sale):
        """Kampanyayı satışa uygular"""
        if not campaign.is_active:
            return None
        
        discount_amount = Decimal('0')
        bonus_amount = None
        
        if campaign.campaign_type in ['student', 'startup']:
            discount_amount = campaign.calculate_discount(sale.amount)
        elif campaign.campaign_type == 'referral':
            bonus_amount = campaign.bonus_amount
        
        return CampaignUsage.objects.create(
            campaign=campaign,
            customer=customer,
            sale=sale,
            discount_amount=discount_amount,
            bonus_amount=bonus_amount
        )
    
    def get_campaign_performance(self, campaign):
        """Kampanya performans analizini döndürür"""
        usages = campaign.usages.all()
        
        return {
            'total_usage': usages.count(),
            'total_discount': usages.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0'),
            'total_bonus': usages.aggregate(total=Sum('bonus_amount'))['total'] or Decimal('0'),
            'unique_customers': usages.values('customer').distinct().count(),
            'avg_discount_per_sale': usages.aggregate(avg=Avg('discount_amount'))['avg'] or Decimal('0'),
            'conversion_rate': self._calculate_conversion_rate(campaign)
        }
    
    def _calculate_conversion_rate(self, campaign):
        """Kampanya dönüşüm oranını hesaplar"""
        total_customers = Customer.objects.filter(
            created_at__range=[campaign.start_date, campaign.end_date]
        ).count()
        
        if total_customers == 0:
            return Decimal('0')
        
        converted_customers = CampaignUsage.objects.filter(
            campaign=campaign
        ).values('customer').distinct().count()
        
        return (Decimal(str(converted_customers)) / Decimal(str(total_customers))) * Decimal('100')
    
    def get_active_campaigns(self):
        """Aktif kampanyaları döndürür"""
        return Campaign.objects.filter(status='active')
    
    def get_expired_campaigns(self):
        """Süresi dolmuş kampanyaları döndürür"""
        today = timezone.now().date()
        return Campaign.objects.filter(end_date__lt=today, status='active')
    
    def update_campaign_status(self):
        """Kampanya durumlarını günceller"""
        today = timezone.now().date()
        
        # Süresi dolan kampanyaları güncelle
        Campaign.objects.filter(
            end_date__lt=today,
            status='active'
        ).update(status='expired')
        
        # Başlangıç tarihi gelen kampanyaları aktifleştir
        Campaign.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status='inactive'
        ).update(status='active')


class RevenueService:
    """Gelir artırıcı önlemler servisi"""
    
    def create_premium_package(self, name, package_type, description, price, billing_cycle, features):
        """Premium paket oluşturur"""
        return PremiumPackage.objects.create(
            name=name,
            package_type=package_type,
            description=description,
            price=price,
            billing_cycle=billing_cycle,
            features=features
        )
    
    def create_consulting_service(self, name, service_type, description, hourly_rate, min_hours):
        """Danışmanlık hizmeti oluşturur"""
        return ConsultingService.objects.create(
            name=name,
            service_type=service_type,
            description=description,
            hourly_rate=hourly_rate,
            min_hours=min_hours
        )
    
    def create_training_program(self, name, program_type, description, duration, 
                              price_per_person, min_participants, max_participants, 
                              materials_included=True):
        """Eğitim programı oluşturur"""
        return TrainingProgram.objects.create(
            name=name,
            program_type=program_type,
            description=description,
            duration=duration,
            price_per_person=price_per_person,
            min_participants=min_participants,
            max_participants=max_participants,
            materials_included=materials_included
        )
    
    def create_api_pricing(self, tier, requests_per_month, price_per_request, base_price, features):
        """API fiyatlandırması oluşturur"""
        return APIPricing.objects.create(
            tier=tier,
            requests_per_month=requests_per_month,
            price_per_request=price_per_request,
            base_price=base_price,
            features=features
        )
    
    def create_subscription(self, customer, subscription_type, start_date, end_date, **kwargs):
        """Hizmet aboneliği oluşturur"""
        subscription = ServiceSubscription(
            customer=customer,
            subscription_type=subscription_type,
            start_date=start_date,
            end_date=end_date
        )
        
        if subscription_type == 'package':
            subscription.package = kwargs.get('package')
            subscription.monthly_fee = subscription.package.price
        elif subscription_type == 'consulting':
            subscription.consulting_service = kwargs.get('consulting_service')
            subscription.monthly_fee = subscription.consulting_service.hourly_rate * subscription.consulting_service.min_hours
        elif subscription_type == 'training':
            subscription.training_program = kwargs.get('training_program')
            subscription.monthly_fee = subscription.training_program.price_per_person * subscription.training_program.min_participants
        elif subscription_type == 'api':
            subscription.api_pricing = kwargs.get('api_pricing')
            subscription.monthly_fee = subscription.api_pricing.base_price + (subscription.api_pricing.price_per_request * subscription.api_pricing.requests_per_month)
        
        subscription.save()
        return subscription
    
    def get_revenue_metrics(self, start_date=None, end_date=None):
        """Gelir metriklerini hesaplar"""
        if not start_date:
            start_date = timezone.now().date().replace(day=1)
        if not end_date:
            end_date = timezone.now().date()
        
        subscriptions = ServiceSubscription.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            status='active'
        )
        
        total_revenue = subscriptions.aggregate(
            total=Sum('monthly_fee')
        )['total'] or Decimal('0')
        
        revenue_by_type = subscriptions.values('subscription_type').annotate(
            total=Sum('monthly_fee'),
            count=Count('id')
        )
        
        active_subscriptions = subscriptions.count()
        avg_revenue_per_subscription = total_revenue / active_subscriptions if active_subscriptions > 0 else Decimal('0')
        
        return {
            'total_revenue': total_revenue,
            'revenue_by_type': revenue_by_type,
            'active_subscriptions': active_subscriptions,
            'avg_revenue_per_subscription': avg_revenue_per_subscription,
            'period': {
                'start': start_date,
                'end': end_date
            }
        }
    
    def get_subscription_performance(self, subscription):
        """Abonelik performans metriklerini hesaplar"""
        if subscription.subscription_type == 'package':
            return self._get_package_performance(subscription)
        elif subscription.subscription_type == 'consulting':
            return self._get_consulting_performance(subscription)
        elif subscription.subscription_type == 'training':
            return self._get_training_performance(subscription)
        elif subscription.subscription_type == 'api':
            return self._get_api_performance(subscription)
        return {}
    
    def _get_package_performance(self, subscription):
        """Paket aboneliği performans metrikleri"""
        return {
            'total_revenue': subscription.monthly_fee,
            'days_active': (timezone.now().date() - subscription.start_date).days,
            'renewal_probability': self._calculate_renewal_probability(subscription)
        }
    
    def _get_consulting_performance(self, subscription):
        """Danışmanlık aboneliği performans metrikleri"""
        return {
            'total_revenue': subscription.monthly_fee,
            'hours_utilized': subscription.consulting_service.min_hours,
            'utilization_rate': 1.0  # Varsayılan olarak %100
        }
    
    def _get_training_performance(self, subscription):
        """Eğitim aboneliği performans metrikleri"""
        return {
            'total_revenue': subscription.monthly_fee,
            'participant_count': subscription.training_program.min_participants,
            'capacity_utilization': subscription.training_program.min_participants / subscription.training_program.max_participants
        }
    
    def _get_api_performance(self, subscription):
        """API aboneliği performans metrikleri"""
        return {
            'total_revenue': subscription.monthly_fee,
            'request_limit': subscription.api_pricing.requests_per_month,
            'utilization_rate': 0.8  # Varsayılan olarak %80
        }
    
    def _calculate_renewal_probability(self, subscription):
        """Yenileme olasılığını hesaplar"""
        # Basit bir hesaplama örneği
        days_active = (timezone.now().date() - subscription.start_date).days
        total_days = (subscription.end_date - subscription.start_date).days
        
        if total_days == 0:
            return 1.0
        
        return min(1.0, days_active / total_days)


class LoyaltyService:
    """Müşteri sadakat programı servisi"""
    
    def create_loyalty_program(self, name, description, points_per_purchase, points_to_currency, min_purchase_for_points):
        """Yeni sadakat programı oluşturur"""
        return LoyaltyProgram.objects.create(
            name=name,
            description=description,
            points_per_purchase=points_per_purchase,
            points_to_currency=points_to_currency,
            min_purchase_for_points=min_purchase_for_points
        )
    
    def add_loyalty_level(self, program, level, min_points, benefits):
        """Sadakat programına yeni seviye ekler"""
        return LoyaltyLevel.objects.create(
            program=program,
            level=level,
            min_points=min_points,
            benefits=benefits
        )
    
    def enroll_customer(self, customer, program):
        """Müşteriyi sadakat programına kaydeder"""
        return CustomerLoyalty.objects.create(
            customer=customer,
            program=program
        )
    
    def calculate_points(self, customer, purchase_amount):
        """Alışveriş için puan hesaplar"""
        loyalty = CustomerLoyalty.objects.get(customer=customer)
        program = loyalty.program
        
        if purchase_amount < program.min_purchase_for_points:
            return 0
            
        points = int(purchase_amount * program.points_per_purchase)
        loyalty.total_points += points
        loyalty.save()
        
        self._check_level_upgrade(loyalty)
        return points
    
    def _check_level_upgrade(self, loyalty):
        """Müşterinin seviye atlayıp atlamadığını kontrol eder"""
        current_level = loyalty.current_level
        program = loyalty.program
        
        for level in program.levels.all():
            if loyalty.total_points >= level.min_points:
                if not current_level or level.min_points > current_level.min_points:
                    loyalty.current_level = level
                    loyalty.save()
                    break
    
    def get_customer_benefits(self, customer):
        """Müşterinin mevcut avantajlarını döndürür"""
        try:
            loyalty = CustomerLoyalty.objects.get(customer=customer)
            if loyalty.current_level:
                return loyalty.current_level.benefits
            return {}
        except CustomerLoyalty.DoesNotExist:
            return {}


class SeasonalCampaignService:
    """Sezonsal kampanya servisi"""
    
    def create_campaign(self, name, campaign_type, description, start_date, end_date, 
                       discount_rate=None, min_purchase_amount=None):
        """Yeni sezonsal kampanya oluşturur"""
        return SeasonalCampaign.objects.create(
            name=name,
            campaign_type=campaign_type,
            description=description,
            start_date=start_date,
            end_date=end_date,
            discount_rate=discount_rate,
            min_purchase_amount=min_purchase_amount
        )
    
    def get_active_campaigns(self):
        """Aktif kampanyaları döndürür"""
        today = timezone.now().date()
        return SeasonalCampaign.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        )
    
    def apply_campaign_discount(self, campaign, purchase_amount):
        """Kampanya indirimini hesaplar"""
        if not campaign.is_active:
            return Decimal('0')
            
        if campaign.min_purchase_amount and purchase_amount < campaign.min_purchase_amount:
            return Decimal('0')
            
        if campaign.discount_rate:
            return purchase_amount * (campaign.discount_rate / Decimal('100'))
        return Decimal('0')


class PartnershipService:
    """İş ortaklığı programı servisi"""
    
    def create_program(self, name, partner_type, description, commission_rate, 
                      min_sales_target, benefits):
        """Yeni iş ortaklığı programı oluşturur"""
        return PartnershipProgram.objects.create(
            name=name,
            partner_type=partner_type,
            description=description,
            commission_rate=commission_rate,
            min_sales_target=min_sales_target,
            benefits=benefits
        )
    
    def register_partner(self, program, company_name, contact_person, email, phone):
        """Yeni iş ortağı kaydı oluşturur"""
        return Partner.objects.create(
            program=program,
            company_name=company_name,
            contact_person=contact_person,
            email=email,
            phone=phone
        )
    
    def calculate_commission(self, partner, sale_amount):
        """Satış komisyonunu hesaplar"""
        commission = sale_amount * (partner.program.commission_rate / Decimal('100'))
        partner.total_sales += sale_amount
        partner.total_commission += commission
        partner.save()
        return commission
    
    def get_partner_performance(self, partner):
        """İş ortağı performans metriklerini döndürür"""
        return {
            'total_sales': partner.total_sales,
            'total_commission': partner.total_commission,
            'target_achievement': (partner.total_sales / partner.program.min_sales_target) * 100,
            'status': partner.get_status_display()
        }
    
    def update_partner_status(self, partner, new_status):
        """İş ortağı durumunu günceller"""
        partner.status = new_status
        partner.save() 