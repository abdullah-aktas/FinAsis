import os
import uuid
import logging
import requests
import json
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import EDocument, Invoice
from abc import ABC, abstractmethod
from django.utils import timezone
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

class EDocumentServiceException(Exception):
    """E-Belge servis entegrasyonu için özel istisna sınıfı"""
    pass

class EDocumentServiceInterface(ABC):
    """E-Belge servis entegrasyonu için soyut temel sınıf"""
    
    @abstractmethod
    def send_invoice(self, invoice, document_type):
        """Faturayı e-belge servisine gönderir"""
        pass
    
    @abstractmethod
    def check_status(self, e_document):
        """E-belge durumunu kontrol eder"""
        pass
    
    @abstractmethod
    def download_pdf(self, e_document):
        """E-belge PDF'ini indirir"""
        pass
    
    @abstractmethod
    def cancel_document(self, e_document, reason):
        """E-belgeyi iptal eder"""
        pass

class BaseEDocumentService(EDocumentServiceInterface):
    """Temel E-Belge Servis sınıfı"""
    
    def __init__(self):
        self.api_key = settings.EDOCUMENT_API_KEY
        self.api_base_url = settings.EDOCUMENT_API_URL
        self.company_vkn = settings.COMPANY_VKN
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def _make_request(self, method, endpoint, data=None, files=None):
        """API isteği yapar ve sonucu döndürür"""
        url = f"{self.api_base_url}/{endpoint}"
        try:
            if method.lower() == 'get':
                response = requests.get(url, headers=self.headers, params=data)
            elif method.lower() == 'post':
                if files:
                    # Dosya yükleme için headers'dan Content-Type çıkarılmalı
                    headers = self.headers.copy()
                    if 'Content-Type' in headers:
                        del headers['Content-Type']
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    response = requests.post(url, headers=self.headers, json=data)
            elif method.lower() == 'put':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.lower() == 'delete':
                response = requests.delete(url, headers=self.headers, json=data)
            else:
                raise EDocumentServiceException(f"Geçersiz HTTP metodu: {method}")
            
            # Yanıt kontrolü
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API isteği başarısız oldu: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_message = error_details.get('message', str(e))
                except ValueError:
                    error_message = e.response.text or str(e)
            else:
                error_message = str(e)
            
            raise EDocumentServiceException(f"Servis hatası: {error_message}")
    
    def _prepare_invoice_data(self, invoice, document_type):
        """Fatura verisini API formatına dönüştürür"""
        # E-Fatura için gerekli veriler
        invoice_lines = []
        for line in invoice.invoice_lines.all():
            invoice_lines.append({
                'name': line.description,
                'quantity': float(line.quantity),
                'unitPrice': float(line.price),
                'vatRate': float(line.vat_rate),
                'total': float(line.total),
                'vatAmount': float(line.vat_amount),
            })
        
        # Fatura alıcı bilgileri
        recipient = {
            'vknTckn': invoice.account.tax_id or '11111111111',
            'name': invoice.account.name,
            'address': invoice.account.address or '',
            'district': invoice.account.district or '',
            'city': invoice.account.city or '',
            'country': invoice.account.country or 'Türkiye',
            'email': invoice.account.email or '',
            'phone': invoice.account.phone or '',
        }
        
        # Fatura ana verisi
        data = {
            'documentType': document_type,
            'documentNumber': invoice.invoice_number,
            'date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'currency': invoice.currency or 'TRY',
            'note': invoice.description or '',
            'issuer': {
                'vknTckn': self.company_vkn,
            },
            'recipient': recipient,
            'items': invoice_lines,
            'totals': {
                'totalWithoutVat': float(invoice.subtotal),
                'vatTotal': float(invoice.vat_total),
                'totalWithVat': float(invoice.total),
            }
        }
        
        return data
    
    def send_invoice(self, invoice, document_type):
        """Faturayı e-belge servisine gönderir"""
        try:
            # Fatura verisini hazırla
            data = self._prepare_invoice_data(invoice, document_type)
            
            # API'ye gönder
            endpoint = 'documents'
            response = self._make_request('post', endpoint, data=data)
            
            # Yanıttan e-belge oluştur
            e_document = EDocument(
                invoice=invoice,
                document_type=document_type,
                document_number=response.get('documentNumber'),
                external_id=response.get('id'),
                status='PENDING',
                xml_content=response.get('xmlContent', ''),
                created_by=invoice.created_by
            )
            e_document.save()
            
            return e_document
            
        except Exception as e:
            logger.error(f"E-Belge gönderimi başarısız oldu: {e}")
            raise EDocumentServiceException(f"E-Belge gönderimi sırasında hata oluştu: {str(e)}")
    
    def check_status(self, e_document):
        """E-belge durumunu kontrol eder"""
        try:
            if not e_document.external_id:
                raise EDocumentServiceException("Belge için servis ID bulunamadı")
            
            endpoint = f"documents/{e_document.external_id}/status"
            response = self._make_request('get', endpoint)
            
            # Durumu güncelle
            status_mapping = {
                'PENDING': 'PENDING',
                'SENT': 'SENT',
                'DELIVERED': 'DELIVERED',
                'READ': 'READ',
                'ACCEPTED': 'ACCEPTED',
                'REJECTED': 'REJECTED',
                'CANCELLED': 'CANCELLED',
                'ERROR': 'ERROR'
            }
            
            new_status = status_mapping.get(response.get('status'), e_document.status)
            e_document.status = new_status
            
            if response.get('statusMessage'):
                e_document.error_message = response.get('statusMessage')
            
            e_document.save()
            return e_document
            
        except Exception as e:
            logger.error(f"E-Belge durum kontrolü başarısız oldu: {e}")
            raise EDocumentServiceException(f"Durum kontrolü sırasında hata oluştu: {str(e)}")
    
    def download_pdf(self, e_document):
        """E-belge PDF'ini indirir"""
        try:
            if not e_document.external_id:
                raise EDocumentServiceException("Belge için servis ID bulunamadı")
            
            endpoint = f"documents/{e_document.external_id}/pdf"
            response = requests.get(f"{self.api_base_url}/{endpoint}", headers=self.headers)
            response.raise_for_status()
            
            # PDF'i kaydet
            filename = f"{e_document.id}.pdf"
            pdf_path = os.path.join('e_documents', 'pdf', filename)
            
            # Dizin yoksa oluştur
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            # Dosyayı kaydet
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # E-belgeyi güncelle
            e_document.pdf_file = pdf_path
            e_document.save()
            
            return e_document
            
        except Exception as e:
            logger.error(f"E-Belge PDF indirme başarısız oldu: {e}")
            raise EDocumentServiceException(f"PDF indirme sırasında hata oluştu: {str(e)}")
    
    def cancel_document(self, e_document, reason):
        """E-belgeyi iptal eder"""
        try:
            if not e_document.external_id:
                raise EDocumentServiceException("Belge için servis ID bulunamadı")
            
            if not e_document.can_be_canceled():
                raise EDocumentServiceException("Bu belge iptal edilemez")
            
            endpoint = f"documents/{e_document.external_id}/cancel"
            data = {"reason": reason}
            response = self._make_request('post', endpoint, data=data)
            
            # Durumu güncelle
            e_document.status = 'CANCELLED'
            e_document.notes = f"İptal nedeni: {reason}"
            e_document.save()
            
            return e_document
            
        except Exception as e:
            logger.error(f"E-Belge iptal işlemi başarısız oldu: {e}")
            raise EDocumentServiceException(f"İptal işlemi sırasında hata oluştu: {str(e)}")

# Farklı entegratörler için alt sınıflar
class EFinansEDocumentService(BaseEDocumentService):
    """E-Finans entegratörü için özel e-belge servisi"""
    
    def __init__(self):
        super().__init__()
        self.headers['X-EFinans-GIB-Code'] = settings.EFINANS_GIB_CODE
    
    def _prepare_invoice_data(self, invoice, document_type):
        """E-Finans için özel veri formatı"""
        data = super()._prepare_invoice_data(invoice, document_type)
        
        # E-Finans'a özel alanlar
        data['profile'] = "TICARIFATURA"
        data['scenario'] = "EARSIVFATURA" if document_type == 'ARCHIVE_INVOICE' else "TEMELFATURA"
        
        return data

class EFaturaEDocumentService(BaseEDocumentService):
    """eFatura entegratörü için özel e-belge servisi"""
    
    def _prepare_invoice_data(self, invoice, document_type):
        """eFatura için özel veri formatı"""
        data = super()._prepare_invoice_data(invoice, document_type)
        
        # eFatura'ya özel alanlar
        data['note'] = f"{data['note']}\nReferans No: {invoice.invoice_number}"
        
        return data

class EArchiveEDocumentService(BaseEDocumentService):
    """E-Arşiv Fatura servis sınıfı"""
    
    def __init__(self):
        super().__init__()
        self.template_name = 'accounting/templates/xml/e_archive.xml'
        self.line_template_name = 'accounting/templates/xml/invoice_line.xml'
    
    def _validate_invoice_data(self, invoice):
        """Fatura verilerinin doğruluğunu kontrol eder"""
        if not invoice.invoice_number:
            raise EDocumentServiceException("Fatura numarası boş olamaz")
            
        if not invoice.invoice_date:
            raise EDocumentServiceException("Fatura tarihi boş olamaz")
            
        if not invoice.account:
            raise EDocumentServiceException("Fatura müşterisi boş olamaz")
            
        if not invoice.account.tax_id:
            raise EDocumentServiceException("Müşteri vergi numarası boş olamaz")
            
        if not invoice.invoice_lines.exists():
            raise EDocumentServiceException("Fatura satırı bulunamadı")
            
        for line in invoice.invoice_lines.all():
            if not line.description:
                raise EDocumentServiceException("Fatura satır açıklaması boş olamaz")
            if not line.quantity or line.quantity <= 0:
                raise EDocumentServiceException("Fatura satır miktarı 0'dan büyük olmalıdır")
            if not line.price or line.price <= 0:
                raise EDocumentServiceException("Fatura satır birim fiyatı 0'dan büyük olmalıdır")
    
    def _prepare_invoice_data(self, invoice, document_type):
        """Fatura verisini API formatına dönüştürür"""
        # Fatura verilerini doğrula
        self._validate_invoice_data(invoice)
        
        # Fatura satırlarını hazırla
        invoice_lines = []
        for line in invoice.invoice_lines.all():
            line_data = {
                'line_id': line.id,
                'item_name': line.description,
                'item_description': line.description,
                'quantity': float(line.quantity),
                'unit_code': line.unit or 'C62',  # C62 = adet
                'unit_price': float(line.price),
                'line_subtotal': float(line.subtotal),
                'line_tax_amount': float(line.vat_amount),
                'line_total': float(line.total),
                'tax_rate': float(line.vat_rate),
                'currency': invoice.currency or 'TRY'
            }
            
            # Satır XML'ini oluştur
            line_xml = render_to_string(self.line_template_name, line_data)
            invoice_lines.append(line_xml)
        
        # Fatura ana verisini hazırla
        data = {
            'invoice_number': invoice.invoice_number,
            'uuid': str(uuid.uuid4()),
            'date': invoice.invoice_date.strftime('%Y-%m-%d'),
            'time': invoice.invoice_date.strftime('%H:%M:%S'),
            'currency': invoice.currency or 'TRY',
            'line_count': len(invoice_lines),
            'company_vkn': self.company_vkn,
            'company_name': settings.COMPANY_NAME,
            'company_website': settings.COMPANY_WEBSITE,
            'company_address': settings.COMPANY_ADDRESS,
            'company_district': settings.COMPANY_DISTRICT,
            'company_city': settings.COMPANY_CITY,
            'company_postal_code': settings.COMPANY_POSTAL_CODE,
            'company_country': settings.COMPANY_COUNTRY,
            'company_tax_office': settings.COMPANY_TAX_OFFICE,
            'company_phone': settings.COMPANY_PHONE,
            'company_email': settings.COMPANY_EMAIL,
            'customer_tckn': invoice.account.tax_id,
            'customer_first_name': invoice.account.first_name,
            'customer_last_name': invoice.account.last_name,
            'customer_address': invoice.account.address,
            'customer_district': invoice.account.district,
            'customer_city': invoice.account.city,
            'customer_postal_code': invoice.account.postal_code,
            'customer_country': invoice.account.country or 'Türkiye',
            'customer_phone': invoice.account.phone,
            'customer_email': invoice.account.email,
            'subtotal': float(invoice.subtotal),
            'tax_total': float(invoice.vat_total),
            'total': float(invoice.total),
            'tax_rate': float(invoice.vat_rate),
            'lines': '\n'.join(invoice_lines)
        }
        
        return data
    
    def send_invoice(self, invoice, document_type='EARSIVFATURA'):
        """Faturayı e-arşiv sistemine gönderir"""
        try:
            # Fatura verisini hazırla
            data = self._prepare_invoice_data(invoice, document_type)
            
            # XML şablonunu doldur
            xml_content = render_to_string(self.template_name, data)
            
            # API'ye gönder
            endpoint = 'documents'
            files = {
                'file': ('invoice.xml', xml_content, 'application/xml')
            }
            response = self._make_request('post', endpoint, files=files)
            
            # Yanıttan e-belge oluştur
            e_document = EDocument(
                invoice=invoice,
                document_type=document_type,
                document_number=response.get('documentNumber'),
                external_id=response.get('id'),
                status='PENDING',
                xml_content=xml_content,
                created_by=invoice.created_by
            )
            e_document.save()
            
            return e_document
            
        except Exception as e:
            logger.error(f"E-Arşiv fatura gönderimi başarısız oldu: {e}")
            raise EDocumentServiceException(f"E-Arşiv fatura gönderimi sırasında hata oluştu: {str(e)}")

# Aktif e-belge servisini al
def get_edocument_service():
    """Yapılandırmaya göre doğru e-belge servisini döndürür"""
    service_type = getattr(settings, 'EDOCUMENT_SERVICE_PROVIDER', 'default')
    
    if service_type == 'efinans':
        return EFinansEDocumentService()
    elif service_type == 'efatura':
        return EFaturaEDocumentService()
    elif service_type == 'earchive':
        return EArchiveEDocumentService()
    else:
        return BaseEDocumentService() 