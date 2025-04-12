from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from decimal import Decimal
import requests
from datetime import date, datetime, timedelta
from django.conf import settings
import logging
from django.db import transaction
from django.core.files.base import ContentFile

from .models import Customer, Opportunity, Activity, Sale, Report, Document
from accounting.models import Account, Invoice, InvoiceLine

logger = logging.getLogger(__name__)


class CustomerAnalyticsService:
    """Müşteri veri analizi servisi"""
    
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